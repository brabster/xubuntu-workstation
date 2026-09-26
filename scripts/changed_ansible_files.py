#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


SCOPE_PATHS = ["roles", "workstation.yml", "workstation.yaml", "test.yml", "test.yaml"]
TOP_LEVEL_PLAYBOOKS = {"workstation.yml", "workstation.yaml", "test.yml", "test.yaml"}
ANSIBLE_ROLE_SUFFIXES = {".yml", ".yaml"}
ZERO_SHA = "0000000000000000000000000000000000000000"


def git_paths(command):
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE)
    return [path.decode("utf-8") for path in result.stdout.split(b"\0") if path]


def selected_files(event_name, diff_base):
    if not diff_base or diff_base == ZERO_SHA:
        return git_paths(["git", "ls-files", "-z", *SCOPE_PATHS])
    if event_name == "pull_request":
        return git_paths(["git", "diff", "--name-only", "-z", f"{diff_base}...HEAD", "--", *SCOPE_PATHS])
    return git_paths(["git", "diff", "--name-only", "-z", f"{diff_base}..HEAD", "--", *SCOPE_PATHS])


def is_scoped_ansible_file(file_path):
    if file_path in TOP_LEVEL_PLAYBOOKS:
        return True
    return file_path.startswith("roles/") and Path(file_path).suffix in ANSIBLE_ROLE_SUFFIXES


def filter_ansible_files(paths):
    for file_path in paths:
        if not is_scoped_ansible_file(file_path):
            continue
        if not Path(file_path).is_file():
            continue
        yield file_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--diff-base", default="")
    parser.add_argument("--null-output", action="store_true")
    args = parser.parse_args()

    for file_path in filter_ansible_files(selected_files(args.event_name, args.diff_base)):
        if args.null_output:
            sys.stdout.write(f"{file_path}\0")
        else:
            print(file_path)


if __name__ == "__main__":
    main()
