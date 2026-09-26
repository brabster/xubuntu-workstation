#!/usr/bin/env python3
from pathlib import Path

import yaml


def ansible_lint_version(config_path):
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    for repo in config.get("repos", []):
        if repo.get("repo") == "https://github.com/ansible/ansible-lint":
            rev = repo.get("rev", "")
            if not rev:
                raise ValueError("ansible-lint repo block is missing rev")
            return str(rev).lstrip("v")
    raise ValueError("ansible-lint repo block not found")


def main():
    print(ansible_lint_version(".pre-commit-config.yaml"))


if __name__ == "__main__":
    main()
