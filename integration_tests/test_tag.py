import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def test_tag(repo_root):
    repo = GitRepo(repo_root)

    # Make sure we are on master
    repo.git.checkout("master")
    head = repo.repo.head.object.hexsha

    # Test tag creation by tagging the current head
    repo.tag.create("test_tag", head)

    # The new tag and "master" references should match
    assert repo.commit.same("test_tag", "master") is True

    # Test tag deletion
    repo.tag.delete("test_tag")

    # Confirm tag doesn't exist anymore
    with pytest.raises(exceptions.ReferenceNotFoundException):
        repo.tag.delete("test_tag")
