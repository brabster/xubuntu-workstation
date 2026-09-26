#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
from pathlib import Path


SCOPE_PATHS = ["roles", "workstation.yml", "workstation.yaml", "test.yml", "test.yaml"]
ANSIBLE_PATH_PATTERN = re.compile(r"^(roles/.*\.ya?ml|workstation\.ya?ml|test\.ya?ml)$")
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


def filter_ansible_files(paths):
    for file_path in paths:
        if not ANSIBLE_PATH_PATTERN.match(file_path):
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
