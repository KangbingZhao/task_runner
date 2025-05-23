import re
import sys

def main():
    commit_msg_file = sys.argv[1]
    with open(commit_msg_file, 'r') as file:
        commit_msg = file.read().strip()

    conventional_commit_regex = r'^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\([a-zA-Z0-9_-]+\))?: .{1,50}$'

    if not re.match(conventional_commit_regex, commit_msg):
        print("ERROR: Commit message does not follow Conventional Commits format.")
        print("Example: feat: add new feature")
        sys.exit(1)

if __name__ == "__main__":
    main()
