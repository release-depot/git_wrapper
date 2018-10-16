import os

import pytest

from git_wrapper.clone import GitWrapperClone
from git_wrapper import exceptions


def test_clone(clone_repo_root, clone_repo_url):
    repo_root = clone_repo_root
    repo_url = clone_repo_url

    clone = GitWrapperClone()

    assert hasattr(clone, "repo") is False

    # Create a new clone
    clone.clone(repo_url, repo_root)

    # Ensure repo has expected tags, some commits
    assert hasattr(clone, "repo") is True

    commit = clone.repo.commit("f8f7abc4ce87db051f9998c5d4dd153695e35675")
    assert commit is not None

    tag = clone.repo.commit("0.1.0")
    assert tag.hexsha == "2e6c014bc296be90a7ed04d155ea7d9da2240bbc"


def test_clone_from_filesystem(clone_repo_root, clone_repo_url, repo_root):
    new_repo_root = clone_repo_root
    repo_url = "file://%s" % repo_root

    clone = GitWrapperClone()

    # Create a new clone
    clone.clone(repo_url, new_repo_root)

    # Ensure repo has expected tags, some commits
    assert hasattr(clone, "repo") is True
    clone.repo.commit("f8f7abc4ce87db051f9998c5d4dd153695e35675")
    tag = clone.repo.commit("0.1.0")
    assert tag.hexsha == "2e6c014bc296be90a7ed04d155ea7d9da2240bbc"


def test_clone_failed(clone_repo_root, clone_repo_url):
    repo_root = clone_repo_root
    repo_url = "http://localhost"

    clone = GitWrapperClone()
    with pytest.raises(exceptions.RepoCreationException):
        clone.clone(repo_url, repo_root)


def test_destroy_and_reclone(clone_repo_root, clone_repo_url):
    repo_root = clone_repo_root
    repo_url = clone_repo_url

    # Start by creating a new repo to destroy
    clone = GitWrapperClone()
    clone.clone(repo_url, repo_root)

    # Get a timestamp for a random file
    f_path = os.path.join(repo_root, 'requirements.txt')
    orig_timestamp = os.path.getmtime(f_path)

    # Run the reclone action
    clone = GitWrapperClone(repo_root)
    clone.destroy_and_reclone()

    # Ensure timestamp changed
    new_timestamp = os.path.getmtime(f_path)
    assert new_timestamp != orig_timestamp
