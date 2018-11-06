import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def test_rebase(repo_root, rebase_cleanup):
    repo = GitRepo(repo_root)
    branch_name = "mybranches/test_repo"
    rebase_to = "2e6c014bc296be90a7ed04d155ea7d9da2240bbc"  # Hash for 0.1.0 tag

    assert repo.repo.active_branch.name == "master"
    assert repo.repo.head.object.hexsha != rebase_to

    # Create a branch based on an old tag
    repo.repo.git.branch(branch_name, "0.0.1")

    # Rebase that branch
    repo.branch.rebase_to_hash(branch_name=branch_name, hash_=rebase_to)
    assert repo.repo.active_branch.name == branch_name
    assert repo.repo.head.object.hexsha == rebase_to


def test_abort_rebase(repo_root, rebase_cleanup):
    repo = GitRepo(repo_root)

    # Set the stage for a failed rebase
    repo.repo.git.checkout("2d88955411f2bd2162f24455f8e948ce435152c5")
    repo.repo.git.cherry_pick("5ded3c1362229c874dea3ac8d63b89b0b104c57a")
    current_head = repo.repo.head.object.hexsha

    # Fail that rebase
    assert repo.repo.is_dirty() is False
    with pytest.raises(exceptions.RebaseException):
        repo.branch.rebase_to_hash(current_head, "31777bbb03da53424c2b0eeae2504a237a4f1720")
    assert repo.repo.is_dirty() is True

    # Perform abort and ensure resulting repo status is clean
    repo.branch.abort_rebase()
    assert repo.repo.is_dirty() is False
    assert repo.repo.head.object.hexsha == current_head


def test_abort_rebase_failure(repo_root):
    repo = GitRepo(repo_root)

    with pytest.raises(exceptions.AbortException):
        repo.branch.abort_rebase()
