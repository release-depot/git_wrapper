#! /usr/bin/env python
"""Tests for GitRepo"""

from mock import Mock, patch, ANY
import shutil

import git
import pytest

from git_wrapper import exceptions
from git_wrapper.branch import GitBranch
from git_wrapper.commit import GitCommit
from git_wrapper.remote import GitRemote
from git_wrapper.repo import GitRepo
from git_wrapper.tag import GitTag


def test_repo(mock_repo):
    """
    GIVEN GitRepo initialized with a path and no repo object
    WHEN the object is created
    THEN a repo added
    """
    with patch('git_wrapper.repo.git') as git_mock:
        attrs = {'Repo.return_value': mock_repo}
        git_mock.configure_mock(**attrs)
        git_util = GitRepo('./')
        assert mock_repo == git_util.repo


def test_not_path_no_repo():
    """
    GIVEN GitRepo initialized with no path or repo object
    WHEN the object is created
    THEN an exception is raised
    """
    with pytest.raises(Exception):
        GitRepo('', None)


def test_git_command(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN the git property is called
    THEN a git object is returned
    """
    git_util = GitRepo('./', mock_repo)

    assert mock_repo.git is git_util.git


def test_remote_setter(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the remote setter is called
    THEN the remote is set as expected
    """
    repo = GitRepo('./', mock_repo)
    new_remote = GitRemote(git_repo=repo, logger=None)
    repo.remote = new_remote
    assert repo.remote == new_remote


def test_remote_setter_wrong_type(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the remote setter is called with the wrong type
    THEN a TypeError is raised
    """
    repo = GitRepo('./', mock_repo)
    with pytest.raises(TypeError):
        repo.remote = repo


def test_branch_setter(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the branch setter is called
    THEN the branch is set as expected
    """
    repo = GitRepo('./', mock_repo)
    new_branch = GitBranch(git_repo=repo, logger=None)
    repo.branch = new_branch
    assert repo.branch == new_branch


def test_branch_setter_wrong_type(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the branch setter is called with the wrong type
    THEN a TypeError is raised
    """
    repo = GitRepo('./', mock_repo)
    with pytest.raises(TypeError):
        repo.branch = repo


def test_commit_setter(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the commit setter is called
    THEN the commit is set as expected
    """
    repo = GitRepo('./', mock_repo)
    new_commit = GitCommit(git_repo=repo, logger=None)
    repo.commit = new_commit
    assert repo.commit == new_commit


def test_commit_setter_wrong_type(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the commit setter is called with the wrong type
    THEN a TypeError is raised
    """
    repo = GitRepo('./', mock_repo)
    with pytest.raises(TypeError):
        repo.commit = repo


def test_tag_setter(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the tag setter is called
    THEN the tag is set as expected
    """
    repo = GitRepo('./', mock_repo)
    new_tag = GitTag(git_repo=repo, logger=None)
    repo.tag = new_tag
    assert repo.tag == new_tag


def test_tag_setter_wrong_type(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the tag setter is called with the wrong type
    THEN a TypeError is raised
    """
    repo = GitRepo('./', mock_repo)
    with pytest.raises(TypeError):
        repo.tag = repo


def test_clone():
    """
    GIVEN GitRepo without a path or repo
    WHEN clone is called with a valid clone_from URL and clone_to path
    THEN Repo.clone_from is called
    """
    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone = GitRepo.clone('./', './testclone')
        assert mock_clone.called is True
        assert isinstance(clone, GitRepo)


def test_bare_clone():
    """
    GIVEN GitRepo without a path or repo
    WHEN clone is called with valid parameters and bare set to True
    THEN Repo.clone_from is called with bare=True
    """
    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        GitRepo.clone('./', './testclone', True)
        mock_clone.assert_called_with('./', ANY, bare=True)


def test_clone_failed():
    """
    GIVEN GitRepo without a path or repo
    WHEN clone is called with a valid clone_from URL and clone_to path
    AND Repo.clone_from fails with an exception
    THEN a RepoCreationException is raised
    """
    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        mock_clone.side_effect = git.GitCommandError('clone', '')
        with pytest.raises(exceptions.RepoCreationException):
            GitRepo.clone('./', './testclone')


def test_destroy_and_reclone(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    THEN Repo.clone_from is called
    WITH the expected remote url and local working dir
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com',
                                      local_dir,
                                      bare=False)


def test_destroy_no_path_no_repo(monkeypatch):
    """
    GIVEN GitRepo initialized with no path or repo object
    WHEN destroy_and_reclone is called
    THEN an exception is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    with pytest.raises(Exception):
        clone = GitRepo('', None)
        clone.destroy_and_reclone()


def test_destroy_no_remotes(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo does not have any remotes configured
    THEN an exception is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)

    with pytest.raises(exceptions.RepoCreationException):
        clone.repo.remotes = {}
        clone.destroy_and_reclone()


def test_destroy_no_remote_named_origin(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo does not have a remote named origin
    THEN Repo.clone_from is called
    WITH the remote url and local working dir from another remote
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697667fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="onlyremote", url="http://example.com/another")
    clone.repo.remotes = [remote]

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com/another',
                                      local_dir,
                                      bare=False)


def test_destroy_and_multiple_remotes(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo has multiple remotes
    THEN Repo.clone_from is called
    AND create_remote is called
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="otherremote", url="http://example.com/another")
    clone.repo.remotes.append(remote)

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        new_repo_mock = Mock()
        mock_clone.return_value = new_repo_mock
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com',
                                      local_dir,
                                      bare=False)
        new_repo_mock.create_remote.assert_called_with(
            "otherremote",
            "http://example.com/another"
        )


def test_destroy_and_remote_creation_fails(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo has several remotes
    AND create_remote fails
    THEN a RemoteException is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="otherremote", url="http://example.com/another")
    clone.repo.remotes.append(remote)

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        new_repo_mock = Mock()
        mock_clone.return_value = new_repo_mock
        with pytest.raises(exceptions.RemoteException):
            new_repo_mock.create_remote.side_effect = git.GitCommandError('remote', '')
            clone.destroy_and_reclone()
        assert mock_clone.called is True
