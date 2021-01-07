import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def test_log_diff(repo_root):
    repo = GitRepo(repo_root)

    log_diff = repo.branch.short_log_diff(
        "155b270a26c5c6cc5e90281fb1a741b293364caa",
        "964aaddddadfbf646fea6a4549e4cb3661a35712"
    )

    assert len(log_diff) == 2
    assert log_diff[0] == "964aadd Drop py34"
    assert log_diff[1] == "5ded3c1 Add basic logging in more places"


def test_log_diff_no_results(repo_root):
    repo = GitRepo(repo_root)

    log_diff = repo.branch.log_diff("0.1.0", "0.1.0")

    assert len(log_diff) == 0


def test_log_diff_wrong_hash(repo_root):
    repo = GitRepo(repo_root)

    with pytest.raises(exceptions.ReferenceNotFoundException):
        repo.branch.log_diff("0.1.0", "123456789z")

    with pytest.raises(exceptions.ReferenceNotFoundException):
        repo.branch.log_diff("123456789z", "0.1.0")


def test_log_grep(repo_root):
    repo = GitRepo(repo_root)

    commits = repo.log.grep_for_commits('master', "Initial commit")

    assert len(commits) == 1
    assert commits[0] == "ba82064c5fea1fc40270fb2748d5d8a783397609"


def test_log_grep_empty(repo_root):
    repo = GitRepo(repo_root)

    commits = repo.log.grep_for_commits('master', "somethingthatcannotbefound", True)

    assert len(commits) == 0


def test_log_grep_with_path(repo_root):
    repo = GitRepo(repo_root)

    commits = repo.log.grep_for_commits('master', "Initial", path=".gitignore")

    assert len(commits) == 1


def test_log_grep_badpath(repo_root):
    repo = GitRepo(repo_root)

    with pytest.raises(exceptions.FileDoesntExistException):
        repo.log.grep_for_commits('master', "Initial", path="badpath")
