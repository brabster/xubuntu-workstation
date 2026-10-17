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
        for branch in ("default", "custom"):
            with self.subTest(branch=branch):
                wm_binding = self.shortcuts.find(
                    f"./property[@name='xfwm4']/property[@name='{branch}']/"
                    "property[@name='<Primary>F2']"
                )
                self.assertIsNotNone(wm_binding)
                self.assertEqual(
                    wm_binding.attrib,
                    {"name": "<Primary>F2", "type": "string", "value": ""},
                )
                command_binding = self.shortcuts.find(
                    f"./property[@name='commands']/property[@name='{branch}']/"
                    "property[@name='<Primary>F2']"
                )
                self.assertIsNotNone(command_binding)
                self.assertEqual(
                    command_binding.attrib,
                    {"name": "<Primary>F2", "type": "string", "value": "xfrun4"},
                )
            for direction in ("Left", "Right", "Up", "Down"):
                with self.subTest(branch=branch, direction=direction):
                    name = f"<Super>KP_{direction}"
                    keypad_binding = self.shortcuts.find(
                        f"./property[@name='xfwm4']/property[@name='{branch}']/"
                        f"property[@name='{name}']"
                    )
                    self.assertIsNotNone(keypad_binding)
                    self.assertEqual(
                        keypad_binding.attrib,
                        {"name": name, "type": "string", "value": ""},
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
      <property name="&lt;Super&gt;KP_Right" type="string" value="tile_right_key"/>
    </property>
    <property name="custom" type="empty">
      <property name="&lt;Primary&gt;&lt;Alt&gt;Left" type="string" value="custom-window-action"/>
      <property name="&lt;Super&gt;KP_Right" type="string" value="tile_right_key"/>
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
        for branch in ("default", "custom"):
            with self.subTest(branch=branch):
                self.assertEqual(
                    properties[("xfwm4", branch, "<Super>KP_Right")], ""
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
        self.assertNotIn("<Alt>Tab", properties)
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


class XfceSessionUpdateTests(unittest.TestCase):
    def setUp(self):
        self.defaults = ET.fromstring(
            """\
<channel name="xfce4-keyboard-shortcuts" version="1.0">
  <property name="commands" type="empty">
    <property name="default" type="empty">
      <property name="&lt;Primary&gt;F2" type="string" value="xfrun4"/>
    </property>
  </property>
  <property name="xfwm4" type="empty">
    <property name="custom" type="empty">
      <property name="&lt;Super&gt;Left" type="string" value="tile_left_key"/>
      <property name="override" type="bool" value="true"/>
    </property>
  </property>
</channel>
"""
        )
        self.managed = [
            ("/commands/default/<Primary>F2", "string", "xfrun4"),
            ("/xfwm4/custom/<Super>Left", "string", "tile_left_key"),
            ("/xfwm4/custom/override", "bool", "true"),
        ]
        self.environment = {
            "DISPLAY": ":17",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
        }
        environment = mock.patch.dict(
            UPDATER.os.environ,
            {
                "DISPLAY": ":17",
                "XDG_RUNTIME_DIR": "/wrong/runtime",
                "DBUS_SESSION_BUS_ADDRESS": "unix:path=/wrong/bus",
            },
            clear=True,
        )
        environment.start()
        self.addCleanup(environment.stop)
        exists = mock.patch.object(Path, "exists", autospec=True, return_value=True)
        self.exists = exists.start()
        self.addCleanup(exists.stop)
        run = mock.patch.object(UPDATER.subprocess, "run")
        self.run = run.start()
        self.addCleanup(run.stop)

    def _query_call(self, path):
        return mock.call(
            [
                "xfconf-query",
                "--channel",
                "xfce4-keyboard-shortcuts",
                "--property",
                path,
            ],
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def _write_call(self, path, value_type, value):
        return mock.call(
            [
                "xfconf-query",
                "--channel",
                "xfce4-keyboard-shortcuts",
                "--property",
                path,
                "--create",
                "--type",
                value_type,
                "--set",
                value,
            ],
            check=True,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def test_unavailable_session_bus_returns_none_without_subprocess_calls(self):
        self.exists.return_value = False

        self.assertIsNone(UPDATER._update_session(self.defaults, 1000))

        self.exists.assert_called_once_with(Path("/run/user/1000/bus"))
        self.run.assert_not_called()

    def test_matching_session_settings_return_false_without_writes(self):
        self.run.side_effect = [
            mock.Mock(returncode=0, stdout=f"  {value}\n")
            for _path, _value_type, value in self.managed
        ]

        self.assertIs(UPDATER._update_session(self.defaults, 1000), False)

        self.exists.assert_called_once_with(Path("/run/user/1000/bus"))
        self.assertEqual(
            self.run.call_args_list,
            [self._query_call(path) for path, _value_type, _value in self.managed],
        )

    def test_changed_and_missing_managed_settings_are_written_with_correct_types(self):
        unrelated = "/commands/custom/<Primary><Alt>t"
        current = {
            self.managed[0][0]: "old-launcher",
            unrelated: "custom-terminal",
        }

        def query_or_write(argv, **kwargs):
            path = argv[argv.index("--property") + 1]
            if kwargs["check"]:
                current[path] = argv[argv.index("--set") + 1]
                return mock.Mock(returncode=0, stdout="")
            return mock.Mock(
                returncode=0 if path in current else 1,
                stdout=current.get(path, ""),
            )

        self.run.side_effect = query_or_write

        self.assertIs(UPDATER._update_session(self.defaults, 1000), True)

        expected = []
        for path, value_type, value in self.managed:
            expected.extend(
                [self._query_call(path), self._write_call(path, value_type, value)]
            )
            self.assertEqual(current[path], value)
        self.assertEqual(self.run.call_args_list, expected)
        self.assertEqual(current[unrelated], "custom-terminal")

    def test_failed_session_write_propagates_called_process_error(self):
        path, value_type, value = self.managed[0]
        write = self._write_call(path, value_type, value)
        error = UPDATER.subprocess.CalledProcessError(
            1, write.args[0], stderr="write denied"
        )
        self.run.side_effect = [
            mock.Mock(returncode=0, stdout="old-launcher\n"),
            error,
        ]

        with self.assertRaises(UPDATER.subprocess.CalledProcessError) as raised:
            UPDATER._update_session(self.defaults, 1000)

        self.assertIs(raised.exception, error)
        self.assertEqual(self.run.call_args_list, [self._query_call(path), write])


if __name__ == "__main__":
    unittest.main()
