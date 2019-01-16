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
