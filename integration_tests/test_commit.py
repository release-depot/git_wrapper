import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def test_describe(repo_root):
    repo = GitRepo(repo_root)

    with pytest.raises(exceptions.ReferenceNotFoundException):
        repo.commit.describe("doesntExist")


def test_revert(repo_root):
    repo = GitRepo(repo_root)
    repo.git.checkout("0.1.0")
    assert "history" in repo.repo.head.object.message

    repo.commit.revert("bf58876c4786fa652432f5902f8b9aef733c2f0a")

    message = repo.repo.head.object.message
    assert "Revert" in message
    assert "history" not in message


def test_revert_with_message(repo_root):
    repo = GitRepo(repo_root)
    repo.git.checkout("0.1.0")
    assert "history" in repo.repo.head.object.message

    repo.commit.revert("bf58876c4786fa652432f5902f8b9aef733c2f0a",
                       message="An explanation for the revert.")

    message = repo.repo.head.object.message
    assert "Revert" in message
    assert "This reverts commit bf5887" in message
    assert "An explanation for the revert" in message


def test_same(repo_root):
    repo = GitRepo(repo_root)

    assert repo.commit.same("0.0.1", "631b3a3") is True
    assert repo.commit.same("0.0.1", "00fed08") is False
