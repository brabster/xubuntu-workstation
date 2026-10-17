"""Real X11 shortcut tests; run only in the dedicated xfce_desktop CI job."""

import json
import os
from pathlib import Path
import pwd
import re
import shutil
import subprocess
import tempfile
import time
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CHANNEL = "xfce4-keyboard-shortcuts"


@unittest.skipUnless(os.environ.get("RUN_XFCE_INTEGRATION") == "1", "needs isolated XFCE")
class XfceDesktopTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(os.geteuid(), 0, "run in CI as root with disposable xfce-ci user")
        self.user = pwd.getpwnam("xfce-ci")
        self.assertNotEqual(self.user.pw_uid, 0)
        self.home = Path(tempfile.mkdtemp(prefix="desktop-", dir=self.user.pw_dir))
        os.chown(self.home, self.user.pw_uid, self.user.pw_gid)
        self.addCleanup(shutil.rmtree, self.home)
        artifacts = Path(os.environ["XFCE_TEST_ARTIFACTS"])
        artifacts.mkdir(parents=True, exist_ok=True)
        self.log = (artifacts / f"{self._testMethodName}.log").open("w")
        self.addCleanup(self.log.close)
        self.runtime = Path(f"/run/user/{self.user.pw_uid}")
        self.runtime.mkdir(mode=0o700, exist_ok=True)
        os.chown(self.runtime, self.user.pw_uid, self.user.pw_gid)
        authority = self.home / ".Xauthority"
        shutil.copyfile(os.environ["XAUTHORITY"], authority)
        os.chown(authority, self.user.pw_uid, self.user.pw_gid)
        self.user_command = [
            "runuser", "-u", self.user.pw_name, "--", "env",
            f"HOME={self.home}", f"XDG_CONFIG_HOME={self.home / '.config'}",
            f"XDG_RUNTIME_DIR={self.runtime}",
            f"DBUS_SESSION_BUS_ADDRESS=unix:path={self.runtime / 'bus'}",
            f"DISPLAY={os.environ['DISPLAY']}", f"XAUTHORITY={authority}",
        ]
        self.processes = []
        self.addCleanup(self.stop_desktop)
        self.write_config("xfconf/xfce-perchannel-xml/xfce4-panel.xml", """\
<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=6;x=0;y=0"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="26"/>
      <property name="plugin-ids" type="array"><value type="int" value="1"/></property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="whiskermenu"/>
  </property>
</channel>
""")
        self.whisker = self.write_config(
            "panel/whiskermenu-1.rc",
            "button-title=Shortcut CI\nshow-button-title=true\nbutton-trigger=1\n",
        )

    def write_config(self, relative, content):
        path = self.home / ".config/xfce4" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        for parent in [path, *path.parents]:
            if parent == self.home:
                break
            os.chown(parent, self.user.pw_uid, self.user.pw_gid)
        return path

    def run_command(self, *args, check=True, desktop=True):
        command = (self.user_command if desktop else []) + list(args)
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        self.log.write(f"$ {command!r}\n{result.stdout}{result.stderr}\n")
        self.log.flush()
        if check:
            self.assertEqual(result.returncode, 0, f"{args!r}: {result.stdout}{result.stderr}")
        return result

    def launch(self, *args):
        process = subprocess.Popen(
            self.user_command + list(args), stdout=self.log, stderr=self.log,
        )
        self.processes.append(process)
        return process

    def wait_for(self, predicate, description):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            result = predicate()
            if result:
                return result
            time.sleep(0.1)
        self.fail(f"Timed out waiting for {description}; see {self.log.name}")

    def start_desktop(self):
        self.launch("dbus-daemon", "--session", "--nofork",
                    f"--address=unix:path={self.runtime / 'bus'}")
        self.wait_for(lambda: (self.runtime / "bus").exists(), "session bus")
        self.launch("xfwm4", "--compositor=off")
        self.wait_for(
            lambda: "window id" in self.run_command(
                "xprop", "-root", "_NET_SUPPORTING_WM_CHECK", check=False
            ).stdout, "XFWM4",
        )
        self.launch("xfsettingsd", "--no-daemon")
        self.launch("xfce4-panel", "--disable-wm-check")
        self.wait_for(
            lambda: "libwhiskermenu" in self.run_command(
                "ps", "-u", str(self.user.pw_uid), "-o", "args="
            ).stdout, "running Whisker plugin",
        )

    def stop_desktop(self):
        if not self.processes:
            return
        self.run_command("xfce4-panel", "--quit", check=False)
        # Shut down xfconfd with SIGTERM so its cached channel is saved, not discarded.
        self.run_command("pkill", "-TERM", "-u", str(self.user.pw_uid),
                         "-x", "xfconfd", check=False, desktop=False)
        time.sleep(0.5)
        self.run_command("pkill", "-TERM", "-u", str(self.user.pw_uid),
                         check=False, desktop=False)
        for process in self.processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.run_command("pkill", "-KILL", "-u", str(self.user.pw_uid),
                                 check=False, desktop=False)
                process.wait(timeout=10)
        self.processes.clear()
        (self.runtime / "bus").unlink(missing_ok=True)

    def apply_role(self):
        environment = os.environ.copy()
        environment["ANSIBLE_ROLES_PATH"] = str(REPO_ROOT / "roles")
        result = subprocess.run(
            [os.environ["ANSIBLE_PLAYBOOK"], "-i", "localhost,",
             str(REPO_ROOT / "tests/integration/xfce.yml"), "-e", json.dumps({
                 "username": self.user.pw_name, "user_home": str(self.home),
                 "ansible_python_interpreter": "/usr/bin/python3",
             })],
            env=environment, capture_output=True, text=True, timeout=120,
        )
        self.log.write(result.stdout + result.stderr)
        self.log.flush()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def shortcut(self, path, value=None, kind="string"):
        args = ["xfconf-query", "-c", CHANNEL, "-p", path]
        if value is not None:
            args += ["--create", "--type", kind, "--set", value]
        return self.run_command(*args).stdout.strip()

    def new_window(self):
        self.launch("xterm", "-T", "shortcut-ci", "-geometry", "40x12+100+100")
        window = self.wait_for(
            lambda: self.run_command(
                "xdotool", "search", "--onlyvisible", "--name", "^shortcut-ci$",
                check=False,
            ).stdout.strip(), "test window",
        )
        self.run_command("xdotool", "windowactivate", "--sync", window)
        return window

    def geometry(self, window):
        result = self.run_command("xwininfo", "-id", window).stdout
        extents = self.run_command("xprop", "-id", window, "_NET_FRAME_EXTENTS").stdout
        left, right, top, bottom = map(int, extents.split("=")[1].split(","))
        values = [int(re.search(pattern + r":\s+(-?\d+)", result).group(1))
                  for pattern in ("Absolute upper-left X", "Absolute upper-left Y",
                                  "Width", "Height")]
        x, y, width, height = values
        return {"X": x - left, "Y": y - top,
                "WIDTH": width + left + right, "HEIGHT": height + top + bottom}

    def tiled(self, window, direction):
        workarea = self.run_command("xprop", "-root", "_NET_WORKAREA").stdout
        x, y, width, height = map(int, workarea.split("=")[1].split(",")[:4])
        expected = {
            "Left": (x, y, width // 2, height),
            "Right": (x + width // 2, y, width // 2, height),
            "Up": (x, y, width, height // 2),
            "Down": (x, y + height // 2, width, height // 2),
        }[direction]
        actual = self.geometry(window)
        # xterm rounds its client size to whole character cells.
        return all(abs(actual[key] - value) <= 20 for key, value in
                   zip(("X", "Y", "WIDTH", "HEIGHT"), expected))

    def check_shortcuts(self):
        window = self.new_window()
        for direction in ("Left", "Right", "Up", "Down"):
            with self.subTest(direction=direction):
                self.run_command("xdotool", "key", "--clearmodifiers", f"super+{direction}")
                self.wait_for(lambda: self.tiled(window, direction), f"Super+{direction} tiling")
        self.run_command("xdotool", "windowclose", window)
        self.run_command("xdotool", "key", "--clearmodifiers", "ctrl+F2")
        launcher = self.wait_for(
            lambda: self.run_command(
                "xdotool", "search", "--onlyvisible", "--class", "[Xx]frun4",
                check=False,
            ).stdout.strip(), "Ctrl+F2 launcher",
        )
        self.run_command("xdotool", "windowclose", launcher)

    def check_whisker_config(self):
        if self.whisker.exists():
            self.assertIn("button-trigger=0", self.whisker.read_text())
        else:
            self.assertEqual(self.run_command(
                "xfconf-query", "-c", "xfce4-panel",
                "-p", "/plugins/plugin-1/button-title",
            ).stdout.strip(), "Shortcut CI")
            self.log.write(
                "Whisker migrated its rc settings to xfconf; this package does not "
                "exercise the rc-file button-trigger setting.\n"
            )

    def test_fresh_profile_and_restart(self):
        self.apply_role()
        self.assertIn("button-trigger=0", self.whisker.read_text())
        self.start_desktop()
        self.check_shortcuts()
        self.stop_desktop()
        self.start_desktop()
        self.check_shortcuts()
        self.assertRegex(self.apply_role(), r"changed=0\s")
        self.check_whisker_config()

    def test_existing_live_profile_and_negative_control(self):
        self.start_desktop()
        self.shortcut("/xfwm4/custom/override", "true", "bool")
        self.shortcut("/xfwm4/custom/<Super>Left", "maximize_window_key")
        self.shortcut("/commands/custom/<Primary><Alt>t", "xterm")
        self.shortcut("/xfwm4/custom/<Primary><Alt>Left", "left_workspace_key")
        self.apply_role()
        self.check_whisker_config()
        # Bootstrap documents logout/login for the Whisker rc-file change.
        self.stop_desktop()
        self.start_desktop()
        self.check_shortcuts()
        self.assertEqual(self.shortcut("/commands/custom/<Primary><Alt>t"), "xterm")
        self.assertEqual(self.shortcut("/xfwm4/custom/<Primary><Alt>Left"), "left_workspace_key")
        self.check_whisker_config()
        self.assertRegex(self.apply_role(), r"changed=0\s")
        self.shortcut("/xfwm4/custom/<Super>Left", "maximize_window_key")
        window = self.new_window()
        self.run_command("xdotool", "key", "--clearmodifiers", "super+Left")
        self.wait_for(
            lambda: self.geometry(window)["WIDTH"] > 1000,
            "deliberately incorrect binding maximizing the window",
        )
        self.assertFalse(self.tiled(window, "Left"), "geometry check must reject a broken binding")


if __name__ == "__main__":
    unittest.main(verbosity=2)
