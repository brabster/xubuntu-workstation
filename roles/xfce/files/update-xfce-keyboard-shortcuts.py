#!/usr/bin/env python3

import argparse
import base64
import copy
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


CHANNEL = "xfce4-keyboard-shortcuts"


def _has_running_xfconfd(uid):
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            if (process / "comm").read_text(encoding="utf-8").strip() == "xfconfd":
                if process.stat().st_uid == uid:
                    return True
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return False


def _has_user_sessions(uid):
    result = subprocess.run(
        ["loginctl", "list-sessions", "--no-legend", "--no-pager"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError("Cannot verify that xfconfd is stopped before offline update")
    return any(
        len(fields := line.split()) > 1 and fields[1] == str(uid)
        for line in result.stdout.splitlines()
    )


def _update_session(defaults, uid):
    bus = Path(f"/run/user/{uid}/bus")
    if not bus.exists():
        return None

    environment = os.environ.copy()
    environment["XDG_RUNTIME_DIR"] = f"/run/user/{uid}"
    environment["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={bus}"
    changed = False
    for section in defaults.findall("property"):
        for branch in section.findall("property"):
            for shortcut in branch.findall("property"):
                path = f"/{section.attrib['name']}/{branch.attrib['name']}/{shortcut.attrib['name']}"
                value = shortcut.attrib["value"]
                current = subprocess.run(
                    ["xfconf-query", "--channel", CHANNEL, "--property", path],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                if current.returncode == 0 and current.stdout.strip() == value:
                    continue
                subprocess.run(
                    [
                        "xfconf-query",
                        "--channel",
                        CHANNEL,
                        "--property",
                        path,
                        "--create",
                        "--type",
                        shortcut.attrib["type"],
                        "--set",
                        value,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                changed = True
    return changed


def _property(parent, name):
    for child in parent.findall("property"):
        if child.attrib.get("name") == name:
            return child
    return ET.SubElement(parent, "property", {"name": name, "type": "empty"})


def _find_property(parent, name):
    for child in parent.findall("property"):
        if child.attrib.get("name") == name:
            return child
    return None


def _merge_defaults(channel, defaults):
    changed = False
    for section in defaults.findall("property"):
        channel_section = _property(channel, section.attrib["name"])
        if section.attrib["name"] == "xfwm4":
            custom = _find_property(channel_section, "custom")
            override = _find_property(custom, "override") if custom is not None else None
            if override is not None and override.attrib.get("value") == "true":
                defaults_default = _find_property(section, "default")
                channel_default = _find_property(channel_section, "default")
                custom = _property(channel_section, "custom")
                if not any(
                    shortcut.attrib.get("name") != "override"
                    for shortcut in custom.findall("property")
                ):
                    for source in (channel_default, defaults_default):
                        if source is not None:
                            for shortcut in source.findall("property"):
                                if _find_property(custom, shortcut.attrib["name"]) is None:
                                    custom.append(copy.deepcopy(shortcut))
                                    changed = True
        for branch in section.findall("property"):
            channel_branch = _find_property(channel_section, branch.attrib["name"])
            if channel_branch is None:
                changed = True
            channel_branch = _property(channel_section, branch.attrib["name"])
            for shortcut in branch.findall("property"):
                target = _find_property(channel_branch, shortcut.attrib["name"])
                if target is None:
                    changed = True
                target = _property(channel_branch, shortcut.attrib["name"])
                for attribute in ("type", "value"):
                    value = shortcut.attrib[attribute]
                    if target.attrib.get(attribute) != value:
                        target.set(attribute, value)
                        changed = True
    return changed


def _file_matches_defaults(path, defaults):
    channel = ET.parse(path).getroot()
    for section in defaults.findall("property"):
        channel_section = _find_property(channel, section.attrib["name"])
        if channel_section is None:
            return False
        for branch in section.findall("property"):
            channel_branch = _find_property(channel_section, branch.attrib["name"])
            if channel_branch is None:
                return False
            for shortcut in branch.findall("property"):
                current = _find_property(channel_branch, shortcut.attrib["name"])
                if current is None or any(
                    current.attrib.get(attribute) != shortcut.attrib[attribute]
                    for attribute in ("type", "value")
                ):
                    return False
    return True


def _update_file(path, defaults, uid):
    if path.exists():
        channel = ET.parse(path).getroot()
        if channel.tag != "channel" or channel.attrib.get("name") != CHANNEL:
            raise RuntimeError(f"Unexpected XFCE channel XML: {path}")
        mode = stat.S_IMODE(path.stat().st_mode)
    else:
        channel = ET.Element("channel", defaults.attrib)
        mode = 0o600

    if not _merge_defaults(channel, defaults):
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            ET.ElementTree(channel).write(
                temporary, encoding="utf-8", xml_declaration=True
            )
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_path, mode)
        if os.stat(path.parent).st_uid == uid:
            os.chown(temporary_path, uid, os.stat(path.parent).st_gid)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return True


def _restore_file(path, original, mode):
    if original is None:
        path.unlink(missing_ok=True)
        return

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(original)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def update(path, defaults):
    uid = os.getuid()
    session_changed = _update_session(defaults, uid)
    if session_changed is not None:
        return session_changed
    if _has_running_xfconfd(uid) or _has_user_sessions(uid):
        raise RuntimeError(
            "No XFCE session bus is available, but the user's session or xfconfd "
            "is active; refusing to update the channel file"
        )
    original = path.read_bytes() if path.exists() else None
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    changed = False
    for _ in range(2):
        changed = _update_file(path, defaults, uid) or changed
        session_changed = _update_session(defaults, uid)
        if session_changed is not None:
            return changed or session_changed
        if _has_running_xfconfd(uid) or _has_user_sessions(uid):
            _restore_file(path, original, mode)
            raise RuntimeError(
                "An XFCE session started during the offline update; retry when its "
                "session bus is available"
            )
        if _file_matches_defaults(path, defaults):
            return changed
    raise RuntimeError("XFCE keyboard shortcuts changed during offline update")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel_file", type=Path)
    parser.add_argument("defaults_xml")
    arguments = parser.parse_args()
    try:
        defaults = ET.fromstring(base64.b64decode(arguments.defaults_xml))
        changed = update(arguments.channel_file, defaults)
    except (ET.ParseError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    print("updated" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
