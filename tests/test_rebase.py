#! /usr/bin/env python

from unittest.mock import patch

import git
import pytest

from git_wrapper import exceptions
from git_wrapper.rebase import GitWrapperRebase


def test_rebase(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN to_hash is called with a valid branch name and a valid hash
    THEN git.checkout called
    AND git.rebase called
    """
    mock_repo.is_dirty.return_value = False
    rebase = GitWrapperRebase('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        rebase.to_hash('test', '12345')

    assert rebase.repo.git.checkout.called is True
    assert rebase.repo.git.rebase.called is True


def test_rebase_dirty_repo(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN to_hash is called on a dirty repository
    THEN a DirtyRepositoryException is raised
    """
    mock_repo.is_dirty.return_value = True
    rebase = GitWrapperRebase('./', mock_repo)

    with pytest.raises(exceptions.DirtyRepositoryException):
        rebase.to_hash('test', '12345')
    assert mock_repo.is_dirty.called is True


def test_rebase_branch_not_found(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN to_hash is called with an invalid branch name
    THEN a ReferenceNotFoundException is raised
    AND the exception message contains branch
    """
    mock_repo.is_dirty.return_value = False
    rebase = GitWrapperRebase('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            mock_name_to_object.side_effect = git.exc.BadName()
            rebase.to_hash('doesNotExist', '12345')
    assert 'branch' in str(exc_info.value)


def test_rebase_hash_not_found(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN to_hash is called with a valid branch name and an invalid hash
    THEN a ReferenceNotFoundException is raised
    AND the exception message contains hash
    """
    mock_repo.is_dirty.return_value = False
    rebase = GitWrapperRebase('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            # First name_to_object call is to check the branch, let it succeed
            def side_effect(mock, ref):
                if ref != "branchA":
                    raise git.exc.BadName
            mock_name_to_object.side_effect = side_effect
            rebase.to_hash('branchA', '12345')
    assert 'hash' in str(exc_info.value)


def test_rebase_error_during_checkout(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN to_hash is called with a valid branch name and a valid hash
    AND checkout fails with an exception
    THEN a CheckoutException is raised
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.checkout.side_effect = git.GitCommandError('checkout', '')
    rebase = GitWrapperRebase('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            rebase.to_hash('branchA', '12345')


def test_rebase_error_during_rebase(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN to_hash is called with a valid branch name and a valid hash
    AND rebase fails with an exception
    THEN a RebaseException is raised
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.rebase.side_effect = git.GitCommandError('rebase', '')
    rebase = GitWrapperRebase('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.RebaseException):
            rebase.to_hash('branchA', '12345')


def test_rebase_abort(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN abort is called
    THEN git.rebase called
    """
    rebase = GitWrapperRebase('./', mock_repo)

    rebase.abort()
    assert rebase.repo.git.rebase.called is True


def test_rebase_abort_error(mock_repo):
    """
    GIVEN GitWrapperRebase initialized with a path and repo
    WHEN abort is called
    AND the abort fails with an exception
    THEN an AbortException is raised
    """
    mock_repo.git.rebase.side_effect = git.GitCommandError('rebase', '')
    rebase = GitWrapperRebase('./', mock_repo)

    with pytest.raises(exceptions.AbortException):
        rebase.abort()
