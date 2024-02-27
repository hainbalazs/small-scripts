"""
importing the pydriller library which is used as a Git API [pip install pydriller]
enclosed underlying functionality:
rev-list --ancestry-path: getting commits from the repository from a to b commit
git log: getting the properties of a given commit
git diff: getting the changes submitted in a given commit
"""
from pydriller import Repository
import os, sys

"""
works as <, > operator in the binary search, to determine whether
* the file is correct, or not existing
    --> we need to look for later commits for the error
    false is returned
* the file is not correct
    --> it might be the commit which caused the error, or we need to look for earlier commits
    true is returned
"""
def good_or_bad(file):
    source = file.source_code
    if not source:
        return False

    # if there are the same amount of opener and closer tags then the file is correct
    open_tag = source.count("<ItemData>")
    close_tag = source.count("</ItemData>")

    return open_tag != close_tag

"""
checks the git diff, and determines whether this was the file, that caused the bug
"""
def caused_bug(file):
    if not file:
        return False
    # the bug is caused due to the omission of a </ItemData>
    # thats why we are looking for that amongst the removed code snippets
    diff = file.diff_parsed['deleted']
    for (line, change) in diff:
        if "</ItemData>" in change:
            return True
    return False

"""
finds the "filters" file amongst the modified files in a given commit
let's suppose there is only one file called "filters" in the whole repository
and it is in the root directory, if not modify the path variable
"""
def find_filters(commit):
    path = "filters"
    for file in commit.modified_files:
        if file.new_path == path:
            return file
    return None

"""
binary search algorithm
"""
def git_bisect(commits):
    l = 0
    r = len(commits) - 1
    while l < r:
        m = (l + r) // 2
        file = find_filters(commits[m])
        caused = caused_bug(file)

        if caused:
            print(f"Found the commit which caused the bug: {commit.hash}")
            return

        elif good_or_bad(file):
             r = m - 1
        else:
             l = m + 1

    print(f"No commit was found which could cause the bug.")


# script usage python git_bin_diff.py [commit_from] [commit_to]

if len(sys.argv) < 3:
    assert("Bad usage of the script, format: python git_bin_diff.py [commit_from] [commit_to]")

commit_from = sys.argv[1]
commit_to = sys.argv[2]

#initializing the repo in the current working tree
repo = Repository(os.getcwd(), from_commit=commit_from, to_commit=commit_to)
commits = list(repo.traverse_commits())
git_bisect(commits)
