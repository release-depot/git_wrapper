import git
import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def test_apply_diff(repo_root, datadir):
    repo = GitRepo(repo_root)
    test_branch = "test_apply_diff"

    # Create a diff file
    diff_path = (datadir / "test.diff")

    # Create a branch from a commit the diff will apply cleanly to
    repo.git.branch(test_branch, "90946e854499ee371c22f6a492fd0f889ae2394f")
    assert repo.repo.active_branch.name == 'master'

    # Apply it
    repo.branch.apply_diff(test_branch, diff_path, "Test commit message", True)

    # Check latest commit
    assert repo.repo.active_branch.name == test_branch
    message = repo.repo.head.object.message
    assert "Test commit message" in message
    assert "Signed-off-by" in message


def test_apply_patch(repo_root, patch_cleanup, datadir):
    repo = GitRepo(repo_root)
    test_branch = "test_apply_patch"

    # Create patch file (based on git format-patch)
    patch_path = (datadir / "test.patch")

    # Create a branch from a commit the patch will apply cleanly to
    repo.git.branch(test_branch, "0.1.0")
    assert repo.repo.active_branch.name == 'master'

    # Apply & check
    repo.branch.apply_patch(test_branch, patch_path)
    assert repo.repo.active_branch.name == test_branch
    assert "Test patch" in repo.repo.head.object.message


def test_abort(repo_root, patch_cleanup, datadir):
    repo = GitRepo(repo_root)
    test_branch = "test_abort"

    # Create a bad patch file
    patch_path = (datadir / "test-bad.patch")

    # Create a branch from a commit
    repo.git.branch(test_branch, "0.1.0")
    assert repo.repo.active_branch.name == 'master'

    # Apply & check for the failure
    with pytest.raises(exceptions.ChangeNotAppliedException):
        repo.branch.apply_patch(test_branch, patch_path)
    assert repo.repo.active_branch.name == test_branch

    # Revert
    repo.branch.abort_patch_apply()
    assert "Test patch" not in repo.repo.head.object.message


def test_reset(repo_root):
    repo = GitRepo(repo_root)
    branch_name = "test_reset"

    # Exercise repo refresh
    repo.remote.fetch("origin")

    # Save the current reference to origin/master
    reset_to_commit = git.repo.fun.name_to_object(repo.repo, "origin/master")

    # Create a new branch based on an old commit
    repo.git.branch(branch_name, "0.0.1")

    # Ensure branch head is different from the one we saved
    branch_commit = repo.repo.branches[branch_name].commit
    assert branch_commit.hexsha != reset_to_commit.hexsha

    # Reset the branch to origin/master
    repo.branch.hard_reset(
        refresh=False,  # Avoid race condition if something new merged
        branch=branch_name,
        remote="origin",
        remote_branch="master"
    )

    # Ensure the new head matches the origin/master we saved
    branch_commit = repo.repo.branches[branch_name].commit
    assert branch_commit.hexsha == reset_to_commit.hexsha


def test_create_branch(repo_root):
    repo = GitRepo(repo_root)
    branch_name = "test_create"
    tag_0_0_1_hexsha = "631b3a35723a038c01669e1933571693a166db81"
    tag_0_1_0_hexsha = "2e6c014bc296be90a7ed04d155ea7d9da2240bbc"

    assert branch_name not in repo.repo.branches

    # Create the new branch
    repo.branch.create(branch_name, "0.0.1")
    assert branch_name in repo.repo.branches
    assert repo.repo.branches[branch_name].commit.hexsha == tag_0_0_1_hexsha

    # Branch already exists - do nothing
    repo.branch.create(branch_name, "0.1.0")
    assert branch_name in repo.repo.branches
    assert repo.repo.branches[branch_name].commit.hexsha == tag_0_0_1_hexsha

    # Branch already exists - reset it
    repo.branch.create(branch_name, "0.1.0", True)
    assert branch_name in repo.repo.branches
    assert repo.repo.branches[branch_name].commit.hexsha == tag_0_1_0_hexsha


def test_create_and_checkout_branch(repo_root):
    repo = GitRepo(repo_root)
    branch_name = "test_create"

    assert repo.repo.active_branch.name == 'master'

    # Create and check out the new branch
    repo.branch.create(branch_name, "0.0.1", checkout=True)
    assert repo.repo.active_branch.name == branch_name

    repo.repo.heads.master.checkout()
    assert repo.repo.active_branch.name == 'master'

    # Branch already exists - reset it and don't check it out
    repo.branch.create(branch_name, "0.1.0", True, checkout=False)
    assert repo.repo.active_branch.name == 'master'

    # Branch already exists - reset it and check it out
    repo.branch.create(branch_name, "0.0.1", True, checkout=True)
    assert repo.repo.active_branch.name == branch_name


def test_remote_contains(repo_root, patch_cleanup, datadir):
    repo = GitRepo(repo_root)
    remote_branch = "origin/master"

    # 1. Check a known commit
    assert repo.branch.remote_contains(
        remote_branch, "fc88bcb3158187ba9566dad896e3c688d8bc5109"
    ) is True

    # 2. Confirm new commit doesn't exist on the remote
    test_branch = "test_contains"
    patch_path = (datadir / "test.patch")
    repo.git.branch(test_branch, "0.1.0")  # For patch to apply cleanly
    repo.branch.apply_patch(test_branch, patch_path)

    assert repo.branch.remote_contains(
        remote_branch, repo.repo.head.object.hexsha
    ) is False
