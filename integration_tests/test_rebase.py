import pytest

from git_wrapper import exceptions
from git_wrapper.rebase import GitWrapperRebase


def test_rebase(repo_root):
    rebase = GitWrapperRebase(repo_root)
    branch_name = "mybranches/test_rebase"
    rebase_to = "2e6c014bc296be90a7ed04d155ea7d9da2240bbc"  # Hash for 0.1.0 tag

    assert rebase.repo.active_branch.name == "master"
    assert rebase.repo.head.object.hexsha != rebase_to

    # Create a branch based on an old tag
    rebase.repo.git.branch(branch_name, "0.0.1")

    # Rebase that branch
    rebase.to_hash(branch_name=branch_name, hash_=rebase_to)
    assert rebase.repo.active_branch.name == branch_name
    assert rebase.repo.head.object.hexsha == rebase_to


def test_abort(repo_root):
    rebase = GitWrapperRebase(repo_root)

    # Set the stage for a failed rebase
    rebase.repo.git.checkout("2d88955411f2bd2162f24455f8e948ce435152c5")
    rebase.repo.git.cherry_pick("5ded3c1362229c874dea3ac8d63b89b0b104c57a")
    current_head = rebase.repo.head.object.hexsha

    # Fail that rebase
    assert rebase.repo.is_dirty() is False
    with pytest.raises(exceptions.RebaseException):
        rebase.to_hash(current_head, "31777bbb03da53424c2b0eeae2504a237a4f1720")
    assert rebase.repo.is_dirty() is True

    # Perform abort and ensure resulting repo status is clean
    rebase.abort()
    assert rebase.repo.is_dirty() is False
    assert rebase.repo.head.object.hexsha == current_head


def test_abort_failure(repo_root):
    rebase = GitWrapperRebase(repo_root)

    with pytest.raises(exceptions.AbortException):
        rebase.abort()
