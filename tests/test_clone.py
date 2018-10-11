#! /usr/bin/env python
"""Tests for GitWrapperClone"""

from mock import patch

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
