#! /usr/bin/env python
"""Tests for GitCommit"""

from mock import patch

import git
import pytest

from git_wrapper.repo import GitRepo
from git_wrapper import exceptions


def test_on_head_only_all_new(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN on_head_only method is called with no upstream equivalent changes
    THEN a dictionary is returned containing two sha1's and commits
    """
    repo = GitRepo('./', mock_repo)
    lines = '+ sha1 commit1\n+ sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha1': 'commit1', 'sha2': 'commit2', 'sha3': 'commit3'}
    assert expected == repo.branch.cherry_on_head_only('upstream', 'HEAD')


def test_on_head_only_with_mixed(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN on_head_only method is called with a mix of
         upstream equivalent and not equivalent changes
    THEN a dictionary is returned containing two sha1's and commits
    """
    repo = GitRepo('./', mock_repo)
    lines = '+ sha1 commit1\n- sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha1': 'commit1', 'sha3': 'commit3'}
    assert expected == repo.branch.cherry_on_head_only('upstream', 'HEAD')


def test_on_head_only_no_new(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN on_head_only method is called with a only upstream equivalent changes
    THEN an empty dictionary is returned
    """
    repo = GitRepo('./', mock_repo)
    lines = '- sha1 commit1\n- sha2 commit2\n- sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == repo.branch.cherry_on_head_only('upstream', 'HEAD')


def test_on_head_only_empty(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN on_head_only is called with no changes
    THEN an empty dictionary is returned
    """
    repo = GitRepo('./', mock_repo)
    lines = ''
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == repo.branch.cherry_on_head_only('upstream', 'HEAD')


def test_all_equivalent_changes(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN equivalent is called with only equivalent upstream/downstream changes.
    THEN a dictionary is returned with all changes
    """
    repo = GitRepo('./', mock_repo)
    lines = '- sha1 commit1\n- sha2 commit2\n- sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha1': 'commit1', 'sha2': 'commit2', 'sha3': 'commit3'}
    assert expected == repo.branch.cherry_equivalent('upstream', 'HEAD')


def test_equivalent_mixed_changes(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN equivalent is called with mix equivalent and HEAD changes.
    THEN a dictionary is returned with only the equivalent changes.
    """
    repo = GitRepo('./', mock_repo)
    lines = '+ sha1 commit1\n- sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha2': 'commit2'}
    assert expected == repo.branch.cherry_equivalent('upstream', 'HEAD')


def test_equivalent_downstream_only(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN equivalent is called with mix HEAD only changes.
    THEN an empty dictionary is returned.
    """
    repo = GitRepo('./', mock_repo)
    lines = '+ sha1 commit1\n+ sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == repo.branch.cherry_equivalent('upstream', 'HEAD')


def test_equivalent_no_changes(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN equivalent is called with no changes.
    THEN an empty dictionary is returned.
    """
    repo = GitRepo('./', mock_repo)
    lines = ''
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == repo.branch.cherry_equivalent('upstream', 'HEAD')


def test_rebase(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.rebase_to_hash is called with a valid branch name and a valid hash
    THEN git.checkout called
    AND git.rebase called
    """
    mock_repo.is_dirty.return_value = False
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.branch.rebase_to_hash('test', '12345')

    assert repo.repo.git.checkout.called is True
    assert repo.repo.git.rebase.called is True


def test_rebase_dirty_repo(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.rebase_to_hash is called on a dirty repository
    THEN a DirtyRepositoryException is raised
    """
    mock_repo.is_dirty.return_value = True
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.DirtyRepositoryException):
            repo.branch.rebase_to_hash('test', '12345')
    assert mock_repo.is_dirty.called is True


def test_rebase_branch_not_found(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.rebase_to_hash is called with an invalid branch name
    THEN a ReferenceNotFoundException is raised
    AND the exception message contains branch
    """
    mock_repo.is_dirty.return_value = False
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            mock_name_to_object.side_effect = git.exc.BadName()
            repo.branch.rebase_to_hash('doesNotExist', '12345')
    assert 'branch' in str(exc_info.value)


def test_rebase_hash_not_found(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.rebase_to_hash is called with a valid branch name and an invalid hash
    THEN a ReferenceNotFoundException is raised
    AND the exception message contains hash
    """
    mock_repo.is_dirty.return_value = False
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            # First name_to_object call is to check the branch, let it succeed
            def side_effect(mock, ref):
                if ref != "branchA":
                    raise git.exc.BadName
            mock_name_to_object.side_effect = side_effect
            repo.branch.rebase_to_hash('branchA', '12345')
    assert 'hash' in str(exc_info.value)


def test_rebase_error_during_checkout(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.rebase_to_hash is called with a valid branch name and a valid hash
    AND checkout fails with an exception
    THEN a CheckoutException is raised
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.checkout.side_effect = git.GitCommandError('checkout', '')
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            repo.branch.rebase_to_hash('branchA', '12345')


def test_rebase_error_during_rebase(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.rebase_to_hash is called with a valid branch name and a valid hash
    AND rebase fails with an exception
    THEN a RebaseException is raised
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.rebase.side_effect = git.GitCommandError('rebase', '')
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.RebaseException):
            repo.branch.rebase_to_hash('branchA', '12345')


def test_abort_rebase(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.abort_rebase is called
    THEN git.rebase called
    """
    repo = GitRepo('./', mock_repo)

    repo.branch.abort_rebase()
    assert repo.repo.git.rebase.called is True


def test_abort_rebase_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN abort_rebase is called
    AND the abort fails with an exception
    THEN an AbortException is raised
    """
    mock_repo.git.rebase.side_effect = git.GitCommandError('rebase', '')
    repo = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.AbortException):
        repo.branch.abort_rebase()
