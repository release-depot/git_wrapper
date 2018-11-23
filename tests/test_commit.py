#! /usr/bin/env python
"""Tests for GitCommit"""

from mock import patch

import git
import pytest

from git_wrapper.repo import GitRepo
from git_wrapper import exceptions


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
    WHEN commit.revert is called with a valid hash_
    THEN git.revert called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.commit.revert('123456')
    assert repo.git.revert.called is True


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
