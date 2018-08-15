#! /usr/bin/env python
"""Tests for GitWrapperCommit"""

from mock import patch

import git
import pytest

from git_wrapper.commit import GitWrapperCommit
from git_wrapper import exceptions


def test_commit(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN commit is called with a valid message
    THEN index.commit called
    """
    commit = GitWrapperCommit('./', mock_repo)
    commit.repo.git.diff.return_value = '+- change'

    commit.commit("My commit message")
    assert commit.repo.git.commit.called is True


def test_commit_no_changes(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN commit is called with a valid message
    AND there are no diff changes
    THEN git.diff called
    AND index.commit not called
    """
    commit = GitWrapperCommit('./', mock_repo)
    commit.repo.git.diff.return_value = []

    commit.commit('my commit message')
    assert commit.repo.git.diff.called is True
    assert commit.repo.git.commit.called is False


def test_commit_no_message(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN commit is called with no valid message
    THEN CommitMessageMissingException raised
    """
    commit = GitWrapperCommit('./', mock_repo)

    with pytest.raises(exceptions.CommitMessageMissingException):
        commit.commit('')


def test_commit_message_is_not_a_string(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN commit is called with no valid message
    THEN CommitMessageMissingException raised
    """
    commit = GitWrapperCommit('./', mock_repo)

    with pytest.raises(exceptions.CommitMessageMissingException):
        commit.commit(True)


def test_revert(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN revert is called with a valid hash_
    THEN git.revert called
    """
    commit = GitWrapperCommit('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        commit.revert('123456')
    assert commit.repo.git.revert.called is True


def test_revert_hash_not_found(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN revert is called
    AND the hash_ doesn't exist
    THEN a ReferenceNotFoundException is raised
    """
    commit = GitWrapperCommit('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            commit.revert('123456')


def test_revert_error(mock_repo):
    """
    GIVEN GitWrapperCommit initialized with a path and repo
    WHEN revert is called
    AND the revert fails with an exception
    THEN a RevertException is raised
    """
    mock_repo.git.revert.side_effect = git.GitCommandError('revert', '')
    commit = GitWrapperCommit('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.RevertException):
            commit.revert('123456')
