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
