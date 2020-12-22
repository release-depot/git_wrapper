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


def test_cherrypick(repo_root):
    repo = GitRepo(repo_root)
    test_branch = "test_cherrypick"
    sha = "130d9974191eda14915e297dc1d797a0580ad2bb"

    # Create a branch from a commit the new sha will apply cleanly to
    repo.git.branch(test_branch, "0.0.1")

    # Cherrypick the commit
    assert repo.repo.active_branch.name == 'master'
    repo.commit.cherrypick(sha, test_branch)
    assert repo.repo.active_branch.name == test_branch

    # Check commit is now the tip of the branch
    message = repo.repo.head.object.message
    assert "GitWrapperCherry" in message


def test_cherrypick_failed(repo_root):
    repo = GitRepo(repo_root)
    test_branch = "test_abort"

    # Create a new branch and confirm the head
    repo.branch.create(test_branch, "0.0.1", checkout=True)
    message = repo.repo.head.object.message
    assert "Adding a wrapper" in message

    # Try to cherry-pick a commit that'll fail
    with pytest.raises(exceptions.ChangeNotAppliedException):
        repo.commit.cherrypick("b615dec08df89ffb9161d6e94aa55cb63e52e3ab", test_branch)

    # Abort and confirm the head is the same as before
    repo.commit.abort_cherrypick()
    message = repo.repo.head.object.message
    assert "Adding a wrapper" in message
