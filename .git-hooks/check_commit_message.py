#!/usr/bin/env python3
import re
import sys

def main():
    commit_msg_file = sys.argv[1]
    with open(commit_msg_file, 'r') as file:
        commit_msg = file.readline().strip()

    conventional_commit_regex = r'^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\([a-zA-Z0-9_-]+\))?: .{1,50}$'

    if not re.match(conventional_commit_regex, commit_msg):
        print("ERROR: Commit message does not follow Conventional Commits format.")
        print("First line was:", repr(commit_msg))
        print("Expected format: <type>(<optional_scope>): <description up to 50 chars>")
        print("Allowed types: feat, fix, docs, style, refactor, test, chore, build, ci, perf, revert")
        print("Example: feat(parser): support new syntax parsing")
        sys.exit(1)

if __name__ == "__main__":
    main()
