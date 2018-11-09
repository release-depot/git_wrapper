#! /usr/bin/env python
"""Tests for GitRemote"""

from mock import Mock

from git import CommandError

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
    mock_repo.create_remote.side_effect = CommandError('create')
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
    update_mock = Mock(side_effect=CommandError('update'))
    remote_mock.attach_mock(update_mock, 'update')

    mock_repo.attach_mock(delete_mock, 'delete_remote')
    mock_repo.create_remote.return_value = remote_mock

    git_util = GitRepo('./', mock_repo)

    assert git_util.remote.add('rdo', 'http://rdoproject.org') is False
    assert update_mock.called is True
    delete_mock.assert_called_once_with(remote_mock)
