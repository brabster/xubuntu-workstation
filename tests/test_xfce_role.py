import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

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

        configure_task = self._task("Configure xfce4 keyboard shortcuts for window tiling")
        self.assertEqual(
            configure_task["ansible.builtin.template"]["src"],
            "xfce4-keyboard-shortcuts.xml.j2",
        )
        self.assertEqual(
            configure_task["ansible.builtin.template"]["mode"],
            "0600",
        )

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
