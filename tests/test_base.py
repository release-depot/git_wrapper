#! /usr/bin/env python
"""Tests for GitWrapperBase"""

from mock import Mock, patch

import pytest

from git import CommandError

from git_wrapper.base import GitWrapperBase


def remote_generator(names):
    '''Generates objects to be used with git.Repo.remotes call'''
    ret_data = []
    for name in names:
        obj = type('', (), {})()
        obj.name = name
        ret_data.append(obj)

    return ret_data


def test_repo(mock_repo):
    """
    GIVEN GitUtilBase initialized with a path and no repo object
    WHEN the object is created
    THEN a repo added
    """
    with patch('git_wrapper.base.git') as git_mock:
        attrs = {'Repo.return_value': mock_repo}
        git_mock.configure_mock(**attrs)
        git_util = GitWrapperBase('./')
        assert mock_repo == git_util.repo


def test_not_path_no_repo():
    """
    GIVEN GitWrapperBase initialized with no path or repo object
    WHEN the object is created
    THEN an exception is raised
    """
    with pytest.raises(Exception):
        GitWrapperBase('', None)


def test_git_command(mock_repo):
    """
    GIVEN GitWrapperBase initialized with a path and repo
    WHEN the git property is called
    THEN a git object is returned
    """
    git_util = GitWrapperBase('./', mock_repo)

    assert mock_repo.git is git_util.git


def test_get_remotes_returns_list(mock_repo):
    """
    GIVEN GitWrapperBase is initialized with a path and repo
    WHEN get_remote_names is called
    THEN a list of remote names is returned
    """
    expected = ['a', 'b', 'c']
    attrs = {'remotes': remote_generator(expected)}
    mock_repo.configure_mock(**attrs)

    git_util = GitWrapperBase('./', mock_repo)

    assert expected == git_util.remote_names()


def test_describe_tag_and_patch(mock_repo):
    """
    GIVEN GitWrapperBase is initialized with a path and repo
    WHEN describe is called with a tag and patch value
    THEN a dictionary with tag and patch keys is returned
    """
    expected = {'tag': '1.0.0', 'patch': '12345'}
    attrs = {'describe.return_value': '1.0.0-g12345'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitWrapperBase('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_tag_only(mock_repo):
    """
    GIVEN GitWrapperBase initialized with a path and repo
    WHEN describe is called a tag value only
    THEN a dictionary with a tag and empty patch is returned
    """
    expected = {'tag': '1.0.0', 'patch': ''}
    attrs = {'describe.return_value': '1.0.0'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitWrapperBase('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_empty(mock_repo):
    """
    GIVEN GitWrapperBase initialized with a path and repo
    WHEN describe is called with a bad hash
    THEN a dictionary with an empty tag and patch is returned
    """
    expected = {'tag': '', 'patch': ''}
    attrs = {'describe.return_value': ''}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitWrapperBase('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_add_remote_adds(mock_repo):
    """
    GIVEN GitWrapperBase initialized with a path and repo
    WHEN add_remote is called with a name and url
    THEN a TRUE status is returned
    WITH update called
    """
    remote_mock = Mock()
    update_mock = Mock()
    remote_mock.attach_mock(update_mock, 'update')
    mock_repo.create_remote.return_value = remote_mock
    git_util = GitWrapperBase('./', mock_repo)

    assert git_util.add_remote('rdo', 'http://rdoproject.org') is True
    assert update_mock.called is True


def test_add_remote_update_fails(mock_repo):
    """
    GIVEN GitWrapperBase initialized with a path and repo
    WHEN add_remote is called with a name and url
    AND the remote update fails with an exception
    THEN a False status is returned
    with delete_remote called
    """
    remote_mock = Mock()
    delete_mock = Mock()
    update_mock = Mock(side_effect=CommandError('update'))
    remote_mock.attach_mock(update_mock, 'update')

    mock_repo.attach_mock(delete_mock, 'delete_remote')
    mock_repo.create_remote.return_value = remote_mock

    git_util = GitWrapperBase('./', mock_repo)

    assert git_util.add_remote('rdo', 'http://rdoproject.org') is False
    assert update_mock.called is True
    delete_mock.assert_called_once_with(remote_mock)
