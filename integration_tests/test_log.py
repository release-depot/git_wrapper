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
