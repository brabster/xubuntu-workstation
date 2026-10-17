import importlib.util
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from unittest import mock

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
XFCE_TASKS = REPO_ROOT / "roles" / "xfce" / "tasks" / "main.yml"
KEYBOARD_SHORTCUTS = (
    REPO_ROOT
    / "roles"
    / "xfce"
    / "templates"
    / "xfce4-keyboard-shortcuts.xml.j2"
)
SHORTCUT_UPDATER = (
    REPO_ROOT / "roles" / "xfce" / "files" / "update-xfce-keyboard-shortcuts.py"
)
SPEC = importlib.util.spec_from_file_location(
    "update_xfce_keyboard_shortcuts", SHORTCUT_UPDATER
)
UPDATER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATER)


class XfceRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = yaml.safe_load(XFCE_TASKS.read_text(encoding="utf-8"))
        cls.shortcuts = ET.fromstring(KEYBOARD_SHORTCUTS.read_text(encoding="utf-8"))

    def _task(self, name):
        for task in self.tasks:
            if task.get("name") == name:
                return task
        self.fail(f"Task not found: {name}")

    def test_keyboard_shortcut_xml_configures_window_tiling(self):
        xfwm4 = self.shortcuts.find("./property[@name='xfwm4']/property[@name='default']")
        shortcuts = {
            prop.attrib["name"]: prop.attrib["value"]
            for prop in xfwm4.findall("property")
        }

        self.assertEqual(shortcuts["<Super>Left"], "tile_left_key")
        self.assertEqual(shortcuts["<Super>Right"], "tile_right_key")
        commands = self.shortcuts.find(
            "./property[@name='commands']/property[@name='default']"
        )
        self.assertEqual(
            commands.find("property").attrib,
            {"name": "<Primary>F2", "type": "string", "value": "xfrun4"},
        )

        configure_task = self._task("Configure xfce4 keyboard shortcuts for window tiling")
        self.assertIn("ansible.builtin.script", configure_task)
        self.assertEqual(configure_task["become_user"], "{{ username }}")

    def test_existing_channel_preserves_unrelated_shortcuts(self):
        existing_xml = """\
<channel name="xfce4-keyboard-shortcuts" version="1.0">
  <property name="commands" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Super&gt;l" type="string" value="custom-lock"/>
      <property name="&lt;Primary&gt;F2" type="string" value="old-launcher"/>
    </property>
    <property name="custom" type="empty">
      <property name="&lt;Primary&gt;&lt;Alt&gt;t" type="string" value="custom-terminal"/>
    </property>
  </property>
  <property name="xfwm4" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Alt&gt;Tab" type="string" value="custom-cycle"/>
      <property name="&lt;Super&gt;Left" type="string" value="old-action"/>
    </property>
    <property name="custom" type="empty">
      <property name="&lt;Primary&gt;&lt;Alt&gt;Left" type="string" value="custom-window-action"/>
    </property>
  </property>
</channel>
"""
        with tempfile.TemporaryDirectory() as directory:
            channel_file = Path(directory) / "xfce4-keyboard-shortcuts.xml"
            channel_file.write_text(existing_xml, encoding="utf-8")
            self.assertTrue(UPDATER._update_file(channel_file, self.shortcuts, 0))
            result = ET.parse(channel_file).getroot()
            properties = {
                (section.attrib["name"], branch.attrib["name"], item.attrib["name"]):
                item.attrib["value"]
                for section in result.findall("property")
                for branch in section.findall("property")
                for item in branch.findall("property")
            }

        self.assertEqual(
            properties[("commands", "default", "<Super>l")], "custom-lock"
        )
        self.assertEqual(
            properties[("commands", "default", "<Primary>F2")], "xfrun4"
        )
        self.assertEqual(
            properties[("commands", "custom", "<Primary><Alt>t")],
            "custom-terminal",
        )
        self.assertEqual(
            properties[("xfwm4", "default", "<Alt>Tab")], "custom-cycle"
        )
        self.assertEqual(
            properties[("xfwm4", "default", "<Super>Left")], "tile_left_key"
        )
        self.assertEqual(
            properties[("xfwm4", "custom", "<Primary><Alt>Left")],
            "custom-window-action",
        )
        self.assertEqual(
            properties[("xfwm4", "custom", "<Super>Left")], "tile_left_key"
        )

    def test_custom_override_preserves_inherited_bindings(self):
        existing_xml = """\
<channel name="xfce4-keyboard-shortcuts" version="1.0">
  <property name="commands" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Primary&gt;F2" type="string" value="old-launcher"/>
    </property>
    <property name="custom" type="empty"/>
  </property>
  <property name="xfwm4" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Super&gt;Up" type="string" value="maximize_window_key"/>
      <property name="&lt;Alt&gt;Tab" type="string" value="cycle_windows_key"/>
    </property>
    <property name="custom" type="empty">
      <property name="override" type="bool" value="true"/>
      <property name="&lt;Super&gt;Left" type="string" value="old-action"/>
      <property name="&lt;Primary&gt;&lt;Alt&gt;Left" type="string" value="custom-action"/>
    </property>
  </property>
</channel>
"""
        with tempfile.TemporaryDirectory() as directory:
            channel_file = Path(directory) / "xfce4-keyboard-shortcuts.xml"
            channel_file.write_text(existing_xml, encoding="utf-8")
            self.assertTrue(UPDATER._update_file(channel_file, self.shortcuts, 0))
            result = ET.parse(channel_file).getroot()
            custom = result.find("./property[@name='xfwm4']/property[@name='custom']")
            commands = result.find("./property[@name='commands']/property[@name='custom']")
            properties = {item.attrib["name"]: item.attrib["value"] for item in custom.findall("property")}

        self.assertEqual(properties["<Super>Left"], "tile_left_key")
        self.assertEqual(properties["<Super>Up"], "tile_up_key")
        self.assertEqual(properties["<Alt>Tab"], "cycle_windows_key")
        self.assertEqual(properties["<Primary><Alt>Left"], "custom-action")
        self.assertEqual(
            commands.find("property").attrib,
            {"name": "<Primary>F2", "type": "string", "value": "xfrun4"},
        )

    def test_missing_custom_branch_is_counted_as_a_change(self):
        channel = ET.fromstring(
            """\
<channel name="xfce4-keyboard-shortcuts" version="1.0">
  <property name="commands" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Primary&gt;F2" type="string" value="xfrun4"/>
    </property>
  </property>
  <property name="xfwm4" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Super&gt;Down" type="string" value="tile_down_key"/>
      <property name="&lt;Super&gt;Left" type="string" value="tile_left_key"/>
      <property name="&lt;Super&gt;Right" type="string" value="tile_right_key"/>
      <property name="&lt;Super&gt;Up" type="string" value="tile_up_key"/>
    </property>
    <property name="custom" type="empty"/>
  </property>
</channel>
"""
        )
        self.assertTrue(UPDATER._merge_defaults(channel, self.shortcuts))

    @mock.patch.object(
        UPDATER.subprocess,
        "run",
        return_value=mock.Mock(returncode=0, stdout="", stderr=""),
    )
    def test_no_sessions_is_valid_for_fully_logged_out_user(self, run):
        self.assertFalse(UPDATER._has_user_sessions(1000))
        self.assertEqual(
            run.call_args.args[0],
            ["loginctl", "list-sessions", "--no-legend", "--no-pager"],
        )

    @mock.patch.object(
        UPDATER.subprocess,
        "run",
        return_value=mock.Mock(
            returncode=0,
            stdout="  12 1000 user seat0 tty2\n  13 1001 other seat1 tty3\n",
            stderr="",
        ),
    )
    def test_user_sessions_are_matched_by_uid(self, _run):
        self.assertTrue(UPDATER._has_user_sessions(1000))
        self.assertFalse(UPDATER._has_user_sessions(1002))

    @mock.patch.object(
        UPDATER.subprocess,
        "run",
        return_value=mock.Mock(returncode=1, stdout="", stderr="failed"),
    )
    def test_session_query_failure_is_rejected(self, _run):
        with self.assertRaisesRegex(RuntimeError, "Cannot verify"):
            UPDATER._has_user_sessions(1000)

    @mock.patch.object(UPDATER, "_update_session", return_value=None)
    @mock.patch.object(UPDATER, "_has_user_sessions", return_value=True)
    @mock.patch.object(UPDATER, "_has_running_xfconfd", return_value=False)
    def test_offline_update_refuses_to_write_during_user_session(
        self, _running_daemon, _user_sessions, _session
    ):
        with tempfile.TemporaryDirectory() as directory:
            channel_file = Path(directory) / "xfce4-keyboard-shortcuts.xml"
            with self.assertRaisesRegex(RuntimeError, "refusing to update"):
                UPDATER.update(channel_file, self.shortcuts)
            self.assertFalse(channel_file.exists())

    @mock.patch.object(UPDATER, "_update_session", side_effect=[None, True])
    @mock.patch.object(UPDATER, "_has_user_sessions", return_value=False)
    @mock.patch.object(UPDATER, "_has_running_xfconfd", return_value=False)
    @mock.patch.object(UPDATER.os, "getuid", return_value=1000)
    def test_session_starting_during_offline_update_is_synchronized(
        self, _uid, _running_daemon, _user_sessions, _session
    ):
        with tempfile.TemporaryDirectory() as directory:
            channel_file = Path(directory) / "xfce4-keyboard-shortcuts.xml"
            self.assertTrue(UPDATER.update(channel_file, self.shortcuts))

    @mock.patch.object(UPDATER, "_file_matches_defaults", side_effect=[False, True])
    @mock.patch.object(UPDATER, "_update_file", return_value=True)
    @mock.patch.object(UPDATER, "_update_session", return_value=None)
    @mock.patch.object(UPDATER, "_has_user_sessions", return_value=False)
    @mock.patch.object(UPDATER, "_has_running_xfconfd", return_value=False)
    @mock.patch.object(UPDATER.os, "getuid", return_value=1000)
    def test_offline_update_retries_if_channel_changes_during_write(
        self,
        _uid,
        _running_daemon,
        _user_sessions,
        _session,
        update_file,
        _matches,
    ):
        self.assertTrue(UPDATER.update(Path("unused"), self.shortcuts))
        self.assertEqual(update_file.call_count, 2)

    @mock.patch.object(UPDATER, "_update_session", return_value=None)
    @mock.patch.object(UPDATER, "_has_user_sessions", side_effect=[False, True])
    @mock.patch.object(UPDATER, "_has_running_xfconfd", return_value=False)
    @mock.patch.object(UPDATER.os, "getuid", return_value=1000)
    def test_raced_session_without_bus_restores_original_channel(
        self, _uid, _running_daemon, _user_sessions, _session
    ):
        original_xml = '<channel name="xfce4-keyboard-shortcuts" version="1.0"/>'
        with tempfile.TemporaryDirectory() as directory:
            channel_file = Path(directory) / "xfce4-keyboard-shortcuts.xml"
            channel_file.write_text(original_xml, encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "session started"):
                UPDATER.update(channel_file, self.shortcuts)
            self.assertEqual(channel_file.read_text(encoding="utf-8"), original_xml)

    def test_whisker_menu_super_trigger_is_disabled_when_config_exists(self):
        find_task = self._task("Find whisker menu panel plugin configuration files")
        self.assertEqual(
            find_task["ansible.builtin.find"]["patterns"],
            "whiskermenu-*.rc",
        )

        disable_task = self._task(
            "Disable whisker menu Super key trigger to allow tile shortcuts"
        )
        lineinfile = disable_task["ansible.builtin.lineinfile"]
        self.assertEqual(lineinfile["regexp"], "^button-trigger=")
        self.assertEqual(lineinfile["line"], "button-trigger=0")
        self.assertEqual(disable_task["loop"], "{{ xfce_whisker_menu_configs.files }}")


if __name__ == "__main__":
    unittest.main()
