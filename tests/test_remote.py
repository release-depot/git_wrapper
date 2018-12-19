#! /usr/bin/env python
"""Tests for GitRemote"""

from mock import Mock

import git
import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def remote_generator(names):
    """Generates objects to be used with git.Repo.remotes call"""
    ret_data = []
    for name in names:
        obj = type('', (), {})()
        obj.name = name
        ret_data.append(obj)

    return ret_data


def test_get_remotes_returns_list(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.names is called
    THEN a list of remote names is returned
    """
    expected = ['a', 'b', 'c']
    attrs = {'remotes': remote_generator(expected)}
    mock_repo.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.remote.names()


def test_add_remote_adds(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN remote.add is called with a name and url
    THEN a TRUE status is returned
    WITH update called
    """
    remote_mock = Mock()
    update_mock = Mock()
    remote_mock.attach_mock(update_mock, 'update')
    mock_repo.create_remote.return_value = remote_mock
    git_util = GitRepo('./', mock_repo)

    assert git_util.remote.add('rdo', 'http://rdoproject.org') is True
    assert update_mock.called is True


def test_add_remote_adds_fails(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN remote.add is called with a name and url
    AND the remote create fails with an exception
    THEN a False status is returned
    """
    mock_repo.create_remote.side_effect = git.CommandError('create')
    git_util = GitRepo('./', mock_repo)

    assert git_util.remote.add('rdo', 'http://rdoproject.org') is False


def test_add_remote_update_fails(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN remote.add is called with a name and url
    AND the remote update fails with an exception
    THEN a False status is returned
    WITH delete_remote called
    """
    remote_mock = Mock()
    delete_mock = Mock()
    update_mock = Mock(side_effect=git.CommandError('update'))
    remote_mock.attach_mock(update_mock, 'update')

    mock_repo.attach_mock(delete_mock, 'delete_remote')
    mock_repo.create_remote.return_value = remote_mock

    git_util = GitRepo('./', mock_repo)

    assert git_util.remote.add('rdo', 'http://rdoproject.org') is False
    assert update_mock.called is True
    delete_mock.assert_called_once_with(remote_mock)


def test_fetch(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch is called
    THEN repo.remote is called
    AND fetch is called
    """
    mock_remote = Mock()
    mock_repo.remote.return_value = mock_remote

    repo = GitRepo(repo=mock_repo)
    repo.remote.fetch()
    assert mock_repo.remote.called is True
    assert mock_remote.fetch.called is True


def test_fetch_remote_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch is called with a remote that doesn't exist
    THEN ReferenceNotFoundException is raised
    """
    mock_repo.remote.side_effect = ValueError

    repo = GitRepo(repo=mock_repo)
    with pytest.raises(exceptions.ReferenceNotFoundException):
        repo.remote.fetch("doesntExist")

    mock_repo.remote.assert_called_with("doesntExist")


def test_fetch_with_fetch_error(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch is called
    AND fetch raises an error
    THEN RemoteException is raised
    """
    mock_remote = Mock()
    mock_remote.fetch.side_effect = git.GitCommandError('fetch', '')
    mock_repo.remote.return_value = mock_remote

    repo = GitRepo(repo=mock_repo)
    with pytest.raises(exceptions.RemoteException):
        repo.remote.fetch("origin")


def test_fetch_all(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch_all is called
    AND there are 2 remotes
    THEN fetch is called twice
    """
    mock_remoteA, mock_remoteB = Mock(), Mock()
    mock_remotes = {"origin": mock_remoteA, "otherremote": mock_remoteB}
    mock_repo.remote = lambda r: mock_remotes[r]

    repo = GitRepo(repo=mock_repo)
    repo.remote.names = Mock(return_value=["origin", "otherremote"])

    repo.remote.fetch_all()
    assert mock_remoteA.fetch.called is True
    assert mock_remoteB.fetch.called is True


def test_fetch_all_with_errors(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch_all is called
    AND one remote fails
    THEN the other remotes still fetch
    AND an exception is raised
    """
    mock_remoteA, mock_remoteB, mock_remoteC = Mock(), Mock(), Mock()
    mock_remoteA.fetch.side_effect = git.GitCommandError("fetch", "")
    mock_remotes = {"origin": mock_remoteA,
                    "a_remote": mock_remoteB,
                    "other": mock_remoteC}
    mock_repo.remote = lambda r: mock_remotes[r]

    repo = GitRepo(repo=mock_repo)
    repo.remote.names = Mock(return_value=["origin", "a_remote", "other"])

    with pytest.raises(exceptions.RemoteException) as exc_info:
        repo.remote.fetch_all()

    assert 'origin' in str(exc_info.value)
    assert mock_remoteA.fetch.called is True
    assert mock_remoteB.fetch.called is True
    assert mock_remoteC.fetch.called is True
