#! /usr/bin/env python
"""Tests for GitLog"""

from mock import patch

import git
import pytest

from git_wrapper.repo import GitRepo
from git_wrapper import exceptions


def test_log_diff(mock_repo, fake_commits):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN log_diff is called with two valid hashes
    THEN a list of log entries is returned
    """
    mock_repo.iter_commits.return_value = fake_commits
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        log_diff = repo.branch.log_diff('12345', '54321')

    assert len(log_diff) == 3
    assert log_diff[2] == (
        "commit 0020000000000000000\n"
        "Author: Test Author <testauthor@example.com>\n"
        "Date: Wed Dec 05 10:36:19 2018 \n\n"
        "This is a commit message (#2)\nWith some details."
    )


def test_short_log_diff(mock_repo, fake_commits):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN short_log_diff is called with two valid hashes
    THEN a list of log entries is returned
    """
    mock_repo.iter_commits.return_value = fake_commits
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        log_diff = repo.branch.short_log_diff('12345', '54321')

    assert len(log_diff) == 3
    assert log_diff == ["0000000 This is a commit message (#0)",
                        "0010000 This is a commit message (#1)",
                        "0020000 This is a commit message (#2)"]


def test_log_diff_with_pattern(mock_repo, fake_commits):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN log_diff is called with two valid hashes and a pattern
    THEN a list of log entries is returned
    """
    mock_repo.iter_commits.return_value = fake_commits
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        log_diff = repo.branch.log_diff('12345', '54321',
                                        pattern="$hash $author")

    assert log_diff == [
        "0000000000000000000 Test Author <testauthor@example.com>",
        "0010000000000000000 Test Author <testauthor@example.com>",
        "0020000000000000000 Test Author <testauthor@example.com>"
    ]


def test_log_diff_no_results(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN log_diff is called with two valid hashes
    AND there are no results
    THEN an empty list is returned
    """
    mock_repo.iter_commits.return_value = []
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        log_diff = repo.branch.log_diff('12345', '12345')

    assert log_diff == []


def test_log_diff_invalid_hash(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN log_diff is called with a invalid hash
    THEN a ReferenceNotFoundException is raised
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException):
            mock_name_to_object.side_effect = git.exc.BadName()
            repo.branch.log_diff('doesNotExist', '12345')

    assert mock_repo.iter_commits.called is False


def test_log_grep(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN log.log_grep_for_commits is called with valid parameters
    THEN a list of commits is returned
    """
    mock_repo.git.log.return_value = "commit1\ncommit2\ncommit3"
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        results = repo.log.grep_for_commits("test_branch", 'test')

    assert results == ["commit1", "commit2", "commit3"]


def test_log_grep_no_commits(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN log.log_grep_for_commits is called with valid parameters
    AND git.log only returns a breakline
    THEN an empty list is returned
    """
    mock_repo.git.log.return_value = ""
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        results = repo.log.grep_for_commits("test_branch", 'test')

    assert results == []


def test_log_grep_with_path(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN log.log_grep_for_commits is called with a valid path
    THEN a list of commits is returned
    """
    mock_repo.git.log.return_value = "commit1"
    mock_repo.tree.return_value = ['testpath', 'test2']
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        results = repo.log.grep_for_commits("test_branch", 'test', True, 'testpath')

    assert results == ["commit1"]


def test_log_grep_bad_path(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN log.log_grep_for_commits is called with an invalid path
    THEN a FileDoesntExist exception is raised
    """
    mock_repo.tree.return_value = ['testpath', 'testpath2']
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.FileDoesntExistException):
            repo.log.grep_for_commits("test_branch", 'test', True, 'wrongpath')
