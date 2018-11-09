#! /usr/bin/env python
"""Tests for GitRepo"""

from mock import patch

import pytest

from git import CommandError

from git_wrapper import exceptions
from git_wrapper.remote import GitRemote
from git_wrapper.repo import GitRepo


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


def test_describe_tag_and_patch(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN describe is called with a tag and patch value
    THEN a dictionary with tag and patch keys is returned
    """
    expected = {'tag': '1.0.0', 'patch': '12345'}
    attrs = {'describe.return_value': '1.0.0-g12345'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_tag_only(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called a tag value only
    THEN a dictionary with a tag and empty patch is returned
    """
    expected = {'tag': '1.0.0', 'patch': ''}
    attrs = {'describe.return_value': '1.0.0'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_empty(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called with a bad hash
    THEN a dictionary with an empty tag and patch is returned
    """
    expected = {'tag': '', 'patch': ''}
    attrs = {'describe.return_value': ''}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_sha_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called with a non-existent hash
    THEN a ReferenceNotFoundException is raised
    """
    git_util = GitRepo('./', mock_repo)
    git_util.git.describe.side_effect = CommandError('describe')

    with pytest.raises(exceptions.DescribeException):
        git_util.describe('12345')


def test_describe_with_lightweight_tags(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called with a good hash for a lightweight tag
    THEN a dictionary with a tag and empty patch is returned
    AND the tag/ prefix is stripped from the tag
    """
    expected = {'tag': '1.0.0-lw', 'patch': ''}
    attrs = {'describe.return_value': 'tag/1.0.0-lw'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


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
