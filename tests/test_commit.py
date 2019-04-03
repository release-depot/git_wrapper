#! /usr/bin/env python
"""Tests for GitCommit"""

from mock import patch

import git
import pytest

from git_wrapper.repo import GitRepo
from git_wrapper import exceptions


def test_describe_tag_and_patch(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN commit.describe is called with a tag and patch value
    THEN a dictionary with tag and patch keys is returned
    """
    expected = {'tag': '1.0.0', 'patch': '12345'}
    attrs = {'describe.return_value': '1.0.0-g12345'}
    mock_repo.git.configure_mock(**attrs)

    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert expected == repo.commit.describe('12345')


def test_describe_tag_only(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.describe is called a tag value only
    THEN a dictionary with a tag and empty patch is returned
    """
    expected = {'tag': '1.0.0', 'patch': ''}
    attrs = {'describe.return_value': '1.0.0'}
    mock_repo.git.configure_mock(**attrs)

    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert expected == repo.commit.describe('12345')


def test_describe_empty(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.describe is called with a bad hash
    THEN a dictionary with an empty tag and patch is returned
    """
    expected = {'tag': '', 'patch': ''}
    attrs = {'describe.return_value': ''}
    mock_repo.git.configure_mock(**attrs)

    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert expected == repo.commit.describe('12345')


def test_describe_sha_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.describe is called with a non-existent hash
    THEN a ReferenceNotFoundException is raised
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.commit.describe('doesntexist')


def test_describe_sha_with_describe_failure(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN git.describe fails
    THEN a DescribeException is raised
    """
    repo = GitRepo('./', mock_repo)
    repo.git.describe.side_effect = git.CommandError('describe')

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.DescribeException):
            repo.commit.describe('12345')


def test_describe_with_lightweight_tags(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.describe is called with a good hash for a lightweight tag
    THEN a dictionary with a tag and empty patch is returned
    AND the tag/ prefix is stripped from the tag
    """
    expected = {'tag': '1.0.0-lw', 'patch': ''}
    attrs = {'describe.return_value': 'tag/1.0.0-lw'}
    mock_repo.git.configure_mock(**attrs)

    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert expected == repo.commit.describe('12345')


def test_commit(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.commit is called with a valid message
    THEN index.commit called
    """
    repo = GitRepo('./', mock_repo)
    repo.git.diff.return_value = '+- change'

    repo.commit.commit("My commit message")
    assert repo.git.commit.called is True


def test_commit_no_changes(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.commit is called with a valid message
    AND there are no diff changes
    THEN git.diff called
    AND index.commit not called
    """
    repo = GitRepo('./', mock_repo)
    repo.git.diff.return_value = []

    repo.commit.commit('my commit message')
    assert repo.git.diff.called is True
    assert repo.git.commit.called is False


def test_commit_no_message(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.commit is called with no valid message
    THEN CommitMessageMissingException raised
    """
    repo = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.CommitMessageMissingException):
        repo.commit.commit('')


def test_commit_message_is_not_a_string(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.commit is called with no valid message
    THEN CommitMessageMissingException raised
    """
    repo = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.CommitMessageMissingException):
        repo.commit.commit(True)


def test_revert(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.revert is called with a valid hash_ and no message
    THEN git.revert called
    AND git.commit is not called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.commit.revert('123456')
    assert repo.git.revert.called is True
    # commit only called when there's a message explicitly included
    assert repo.git.commit.called is False


def test_revert_hash_not_found(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.revert is called
    AND the hash_ doesn't exist
    THEN a ReferenceNotFoundException is raised
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.commit.revert('123456')


def test_revert_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.revert is called
    AND the revert fails with an exception
    THEN a RevertException is raised
    """
    mock_repo.git.revert.side_effect = git.GitCommandError('revert', '')
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.RevertException):
            repo.commit.revert('123456')


def test_revert_with_message(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN commit.revert is called with a valid hash_ and a message
    THEN git.revert is called
    AND git.commit is called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.commit.revert('123456', "My message")
    assert repo.git.revert.called is True
    assert repo.git.commit.called is True
