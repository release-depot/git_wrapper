import git
import pytest


REPO_ROOT = "/tests/git_wrapper"


@pytest.fixture(scope="function")
def repo_root():
    # Check the starting point is sane
    repo = git.Repo(REPO_ROOT)
    origin = repo.remotes.origin

    repo.heads.master.checkout()
    assert repo.head.object == origin.refs.master.object
    assert repo.is_dirty() is False

    yield REPO_ROOT

    # Reset current changes and master branch to original state
    repo.head.reset(index=True, working_tree=True)
    repo.heads.master.checkout()
    repo.head.reset(origin.refs.master, index=True, working_tree=True)
