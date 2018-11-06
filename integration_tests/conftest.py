import shutil

import git
import pytest


CLONE_REPO_ROOT = "/tests/cloning_tests"
CLONE_REPO_URL = "https://github.com/release-depot/git_wrapper"
REPO_ROOT = "/tests/git_wrapper"  # Local copy


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

    # Remove extra local branches
    for b in repo.branches:
        if b.name != 'master':
            repo.git.branch("-D", b.name)


@pytest.fixture(scope="function")
def clone_repo_root():
    # We use a different repo root for cloning tests, because some of
    # the tests are destructive and we don't want to inadvertently
    # delete the test copy of the repo that contains the patch being tested
    yield CLONE_REPO_ROOT
    shutil.rmtree(CLONE_REPO_ROOT, ignore_errors=True)


@pytest.fixture
def clone_repo_url():
    yield CLONE_REPO_URL


@pytest.fixture(scope="function")
def patch_cleanup():
    # Avoid state leaking into other tests in case of early failure
    yield
    repo = git.Repo(REPO_ROOT)
    try:
        repo.git.am('--abort')
    except git.GitCommandError:
        pass


@pytest.fixture(scope="function")
def rebase_cleanup():
    # Avoid state leaking into other tests in case of early failure
    yield
    repo = git.Repo(REPO_ROOT)
    try:
        repo.git.rebase('--abort')
    except git.GitCommandError:
        pass
