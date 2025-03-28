#! /usr/bin/env python
"""Tests for GitRemote"""

from dataclasses import dataclass
from mock import Mock

import git
import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


@dataclass
class RemoteNames:
    name: str


@dataclass
class RemoteNamesUrl(RemoteNames):
    url: str


def remote_generator(names):
    """Generates objects to be used with git.Repo.remotes call"""
    ret_data = []
    for name in names:
        ret_data.append(RemoteNames(name))
    return ret_data


def remote_generator_url(remotes):
    """Generates objects to be used with git.Repo.remotes call"""
    ret_data = []
    for name, url in remotes.items():
        ret_data.append(RemoteNamesUrl(name, url))
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


def test_get_remotes_returns_dict(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.names_url_dict is called
    THEN a dict of remote names with its url is returned
    """
    expected = {'a': 1, 'b': 2, 'c': 3}
    attrs = {'remotes': remote_generator_url(expected)}
    mock_repo.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.remote.names_url_dict()


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


def test_remove_remote_removes(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN remote.remove is called with a name and url
    THEN a TRUE status is returned
    """
    git_util = GitRepo('./', mock_repo)

    assert git_util.remote.remove('origin') is True


def test_remove_remote_remote_fails(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN remote.remove is called with a name and url
    AND the repo.remote fails with an exception
    THEN a ReferenceNotFoundException is raised
    """
    mock_repo.remote.side_effect = ValueError

    repo = GitRepo(repo=mock_repo)
    with pytest.raises(exceptions.ReferenceNotFoundException):
        repo.remote.remove("doesntExist")

    mock_repo.remote.assert_called_with("doesntExist")


def test_remove_remote_remove_fails(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN remote.remove is called with a name and url
    AND the repo.delete_remote fails with an exception
    THEN a False status is returned
    """
    mock_repo.delete_remote.side_effect = git.CommandError('remove')
    git_util = GitRepo('./', mock_repo)

    assert git_util.remote.remove('rdo') is False


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

    mock_repo.remote.assert_called()
    mock_remote.fetch.assert_called()
    mock_remote.fetch.assert_called_with(prune=False, prune_tags=False)


def test_fetch_prune(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch is called
    AND prune is True
    THEN repo.remote is called
    AND fetch is called with prune
    """
    mock_remote = Mock()
    mock_repo.remote.return_value = mock_remote

    repo = GitRepo(repo=mock_repo)
    repo.remote.fetch(prune=True)

    mock_repo.remote.assert_called()
    mock_remote.fetch.assert_called()
    mock_remote.fetch.assert_called_with(prune=True, prune_tags=False)


def test_fetch_prune_tags(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch is called
    AND prune and prune_tags are True
    THEN repo.remote is called
    AND fetch is called with prune and prune_tags
    """
    mock_remote = Mock()
    mock_repo.remote.return_value = mock_remote

    repo = GitRepo(repo=mock_repo)
    repo.remote.fetch(prune=True, prune_tags=True)

    mock_repo.remote.assert_called()
    mock_remote.fetch.assert_called()
    mock_remote.fetch.assert_called_with(prune=True, prune_tags=True)


def test_fetch_no_prune(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch is called
    AND prune_tags is True but prune is False
    THEN repo.remote is called
    AND fetch is called without prune and prune_tags
    """
    mock_remote = Mock()
    mock_repo.remote.return_value = mock_remote

    repo = GitRepo(repo=mock_repo)
    repo.remote.fetch(prune=False, prune_tags=True)

    mock_repo.remote.assert_called()
    mock_remote.fetch.assert_called()
    mock_remote.fetch.assert_called_with()


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

    mock_remoteA.fetch.assert_called()
    mock_remoteB.fetch.assert_called()


def test_fetch_all_prune(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch_all is called
    AND there are 2 remotes
    AND prune is True
    THEN fetch is called twice with prune
    """
    mock_remoteA, mock_remoteB = Mock(), Mock()
    mock_remotes = {"origin": mock_remoteA, "otherremote": mock_remoteB}
    mock_repo.remote = lambda r: mock_remotes[r]

    repo = GitRepo(repo=mock_repo)
    repo.remote.names = Mock(return_value=["origin", "otherremote"])

    repo.remote.fetch_all(prune=True)

    mock_remoteA.fetch.assert_called()
    mock_remoteB.fetch.assert_called()
    mock_remoteA.fetch.assert_called_with(prune=True, prune_tags=False)
    mock_remoteB.fetch.assert_called_with(prune=True, prune_tags=False)


def test_fetch_all_prune_tags(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN remote.fetch_all is called
    AND there are 2 remotes
    AND prune and prune_tags are True
    THEN fetch is called twice with prune and prune_tags
    """
    mock_remoteA, mock_remoteB = Mock(), Mock()
    mock_remotes = {"origin": mock_remoteA, "otherremote": mock_remoteB}
    mock_repo.remote = lambda r: mock_remotes[r]

    repo = GitRepo(repo=mock_repo)
    repo.remote.names = Mock(return_value=["origin", "otherremote"])

    repo.remote.fetch_all(prune=True, prune_tags=True)

    mock_remoteA.fetch.assert_called()
    mock_remoteB.fetch.assert_called()
    mock_remoteA.fetch.assert_called_with(prune=True, prune_tags=True)
    mock_remoteB.fetch.assert_called_with(prune=True, prune_tags=True)


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

    mock_remoteA.fetch.assert_called()
    mock_remoteB.fetch.assert_called()
    mock_remoteC.fetch.assert_called()
