import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml
from jinja2 import Environment


REPO_ROOT = Path(__file__).resolve().parents[1]
ROLE_DIR = REPO_ROOT / "roles" / "lxqt_labwc"


class LxqtLabwcRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.defaults = yaml.safe_load(
            (ROLE_DIR / "defaults" / "main.yml").read_text(encoding="utf-8")
        )
        cls.tasks = yaml.safe_load(
            (ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
        )

    def _task(self, name):
        for task in self.tasks:
            if task.get("name") == name:
                return task
        self.fail(f"Task not found: {name}")

    def test_installs_only_required_packages_without_recommends(self):
        install = self._task("Install LXQt Wayland desktop and verification packages")[
            "ansible.builtin.apt"
        ]
        self.assertEqual(
            install["name"],
            [
                "lxqt-core",
                "lxqt-wayland-session",
                "labwc",
                "qterminal",
                "swaylock",
                "wtype",
                "procps",
            ],
        )
        self.assertFalse(install["install_recommends"])

    def test_configuration_directories_and_files_have_private_modes(self):
        directories = self._task("Ensure LXQt configuration directories are private")
        self.assertEqual(directories["ansible.builtin.file"]["mode"], "0700")
        self.assertEqual(
            directories["loop"], ["", "lxqt", "labwc", "environment.d"]
        )
        for name in (
            "Configure LXQt Wayland session",
            "Configure Wayland environment",
            "Configure labwc keyboard shortcuts",
        ):
            module = next(
                value
                for key, value in self._task(name).items()
                if key in ("ansible.builtin.copy", "ansible.builtin.template")
            )
            self.assertEqual(module["mode"], "0600")

    def test_session_and_environment_select_wayland_and_swaylock(self):
        session = self._task("Configure LXQt Wayland session")[
            "ansible.builtin.copy"
        ]["content"]
        environment = self._task("Configure Wayland environment")[
            "ansible.builtin.copy"
        ]["content"]

        for setting in (
            "DisplayServer=wayland",
            "CompositorCommand=labwc",
            "ScreenLocker=swaylock -f -c 000000",
        ):
            self.assertIn(setting, session)
        for setting in (
            "ELECTRON_OZONE_PLATFORM_HINT=auto",
            "MOZ_ENABLE_WAYLAND=1",
            "QT_QPA_PLATFORM=wayland;xcb",
        ):
            self.assertIn(setting, environment)

    def test_shortcuts_render_valid_xml_with_absolute_commands(self):
        template = Environment().from_string(
            (ROLE_DIR / "templates" / "rc.xml.j2").read_text(encoding="utf-8")
        )
        rendered = template.render(**self.defaults)
        root = ET.fromstring(rendered)
        keybinds = root.findall("./keyboard/keybind")

        self.assertEqual(len(keybinds), 2)
        self.assertIsNotNone(root.find("./keyboard/default"))
        for shortcut in keybinds:
            action = shortcut.find("./action")
            self.assertTrue(action.attrib["command"].startswith("/"))

    def test_molecule_verifies_static_config_and_headless_shortcut(self):
        verify = yaml.safe_load(
            (ROLE_DIR / "molecule" / "default" / "verify.yml").read_text(
                encoding="utf-8"
            )
        )[0]["tasks"]
        static_gate = verify[0]["ansible.builtin.command"]["argv"]
        self.assertEqual(static_gate, ["labwc", "-C", "{{ ansible_facts['user_dir'] }}/.config/labwc", "-m"])

        behavioral_gate = verify[1]["ansible.builtin.shell"]["cmd"]
        for requirement in (
            "WLR_BACKENDS=headless",
            "WLR_RENDERER=pixman",
            'mktemp -d /tmp/wayland-ci.XXXXXX',
            'trap \'rm -rf "$XDG_RUNTIME_DIR"\' EXIT',
            "wtype -M logo -k Return -m logo",
            "pgrep -u $(id -u) -x qterminal",
            "labwc -e",
        ):
            self.assertIn(requirement, behavioral_gate)


if __name__ == "__main__":
    unittest.main()
