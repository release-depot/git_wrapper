#! /usr/bin/env python
"""Tests for GitWrapperClone"""

from mock import mock, patch
import shutil

import git
import pytest

from git_wrapper.clone import GitWrapperClone
from git_wrapper import exceptions


def test_clone():
    """
    GIVEN GitWrapperClone initialized without a path or repo
    WHEN clone is called with a valid clone_from URL and clone_to path
    THEN Repo.clone_from is called
    """
    clone = GitWrapperClone()

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.clone('./', './testclone')
        assert mock_clone.called is True


def test_clone_failed():
    """
    GIVEN GitWrapperClone initialized with a path or repo
    WHEN clone is called with a valid clone_from URL and clone_to path
    AND Repo.clone_from fails with an exception
    THEN a RepoCreationException is raised
    """
    clone = GitWrapperClone()

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        mock_clone.side_effect = git.GitCommandError('clone', '')
        with pytest.raises(exceptions.RepoCreationException):
            clone.clone('./', './testclone')


def test_destroy_and_reclone(mock_repo, monkeypatch):
    """
    GIVEN GitWrapperClone initialized with a path and repo
    WHEN destroy_and_reclone is called
    THEN Repo.clone_from is called
    WITH the expected remote url and local working dir
    """
    monkeypatch.setattr(shutil, 'rmtree', mock.Mock())
    clone = GitWrapperClone(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        assert mock_clone.called_with('http://example.com', local_dir)


def test_destroy_no_path_no_repo(monkeypatch):
    """
    GIVEN GitWrapperClone initialized with no path or repo object
    WHEN destroy_and_reclone is called
    THEN an exception is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', mock.Mock())
    with pytest.raises(Exception):
        clone = GitWrapperClone('', None)
        clone.destroy_and_reclone()


def test_destroy_no_remotes(mock_repo, monkeypatch):
    """
    GIVEN GitWrapperClone initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo does not have any remotes configured
    THEN an exception is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', mock.Mock())
    clone = GitWrapperClone(repo=mock_repo)

    with pytest.raises(exceptions.RepoCreationException):
        clone.repo.remotes = {}
        clone.destroy_and_reclone()


def test_destroy_no_remote_named_origin(mock_repo, monkeypatch):
    """
    GIVEN GitWrapperClone initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo does not have a remote named origin
    THEN Repo.clone_from is called
    WITH the remote url and local working dir from another remote
    """
    monkeypatch.setattr(shutil, 'rmtree', mock.Mock())
    clone = GitWrapperClone(repo=mock_repo)
    local_dir = '/tmp/8f697667fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = mock.Mock(spec=git.Remote)
    remote.configure_mock(name="onlyremote", url="http://example.com/another")
    clone.repo.remotes = [remote]

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com/another', local_dir)


def test_destroy_and_multiple_remotes(mock_repo, monkeypatch):
    """
    GIVEN GitWrapperClone initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo has multiple remotes
    THEN Repo.clone_from is called
    AND create_remote is called
    """
    monkeypatch.setattr(shutil, 'rmtree', mock.Mock())
    clone = GitWrapperClone(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = mock.Mock(spec=git.Remote)
    remote.configure_mock(name="otherremote", url="http://example.com/another")
    clone.repo.remotes.append(remote)

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        new_repo_mock = mock.Mock()
        mock_clone.return_value = new_repo_mock
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com', local_dir)
        new_repo_mock.create_remote.assert_called_with(
            "otherremote",
            "http://example.com/another"
        )


def test_destroy_and_remote_creation_fails(mock_repo, monkeypatch):
    """
    GIVEN GitWrapperClone initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo has several remotes
    AND create_remote fails
    THEN a RemoteException is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', mock.Mock())
    clone = GitWrapperClone(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = mock.Mock(spec=git.Remote)
    remote.configure_mock(name="otherremote", url="http://example.com/another")
    clone.repo.remotes.append(remote)

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        new_repo_mock = mock.Mock()
        mock_clone.return_value = new_repo_mock
        with pytest.raises(exceptions.RemoteException):
            new_repo_mock.create_remote.side_effect = git.GitCommandError('remote', '')
            clone.destroy_and_reclone()
        assert mock_clone.called is True
