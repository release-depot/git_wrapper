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


def test_apply_patch(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch_name and valid path
    THEN git.am is called
    """
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        commit.commit.apply_patch('test_branch', './requirements.txt')
    assert commit.repo.git.am.called is True


def test_apply_patch_wrong_branch_name(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with an invalid branch_name and valid path
    THEN ReferenceNotFoundExceptionRaised
    AND git.am not called
    """
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            commit.commit.apply_patch('invalid_branch', './requirements.txt')
    assert commit.repo.git.am.called is False


def test_apply_patch_not_a_file(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch_name and invalid path
    THEN FileDoesntExistException raised
    AND git.am not called
    """
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.FileDoesntExistException):
            commit.commit.apply_patch('test_branch', './git_wrapper')
    assert commit.repo.git.am.called is False


def test_apply_patch_checkout_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch name and a valid path
    AND checkout fails with an exception
    THEN a CheckoutException is raised
    AND git.am not called
    """
    mock_repo.git.checkout.side_effect = git.GitCommandError('checkout', '')
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            commit.commit.apply_patch('test_branch', './requirements.txt')
    assert commit.repo.git.am.called is False


def test_apply_patch_apply_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch name and a valid path
    AND git.am fails with an exception
    THEN a ChangeNotAppliedException is raised
    """
    mock_repo.git.am.side_effect = git.GitCommandError('am', '')
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.ChangeNotAppliedException):
            commit.commit.apply_patch('test_branch', './requirements.txt')


def test_apply_diff(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with a valid branch_name and valid diff_path and valid message
    THEN index.commit is called
    """
    mock_repo.is_dirty.return_value = False
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        commit.commit.apply_diff('test_branch', './requirements.txt', 'message', True)
    assert commit.repo.git.apply.called is True
    assert commit.repo.git.commit.called is True


def test_apply_diff_on_invalid_branch(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with an invalid branch_name and valid path
    THEN ReferenceNotFoundExceptionRaised
    AND git.apply not called
    """
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            commit.commit.apply_diff('invalid_branch', './requirements.txt', 'message')
    assert commit.repo.git.apply.called is False


def test_apply_diff_on_dirty_workspace(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called on a dirty repository
    THEN a DirtyRepositoryException is raised
    AND git.apply not called
    """
    mock_repo.is_dirty.return_value = True
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.DirtyRepositoryException):
            commit.commit.apply_diff('test_branch', './requirements.txt', 'message')
    assert mock_repo.is_dirty.called is True
    assert commit.repo.git.apply.called is False


def test_apply_diff_no_commit_message(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with valid branch_name, valid diff_path and invalid message
    THEN CommitMessageMissingException raised
    AND index.commit not called
    """
    mock_repo.is_dirty.return_value = False
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CommitMessageMissingException):
            commit.commit.apply_diff('test_branch', './requirements.txt', '')
    assert commit.repo.git.commit.called is False


def test_apply_diff_not_a_file(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with valid parameters
    THEN FileDoesntExistException raised
    AND git.apply not called
    """
    mock_repo.is_dirty.return_value = False
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.FileDoesntExistException):
            commit.commit.apply_diff('test_branch', 'doesntexist.txt', 'message')
    assert commit.repo.git.apply.called is False


def test_apply_diff_checkout_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with valid parameters
    AND checkout fails with an exception
    THEN a CheckoutException is raised
    AND index.commit not called
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.checkout.side_effect = git.GitCommandError('checkout', '')
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            commit.commit.apply_diff('invalid_branch', './requirements.txt', 'my message')
    assert commit.repo.git.commit.called is False


def test_apply_diff_apply_fails(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with a valid branch_name and valid diff_path and valid message
    AND git.apply fails with an exception
    THEN an ChangeNotAppliedException is raised
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.apply.side_effect = git.GitCommandError('apply', '')
    commit = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.ChangeNotAppliedException):
            commit.commit.apply_diff('test_branch', './requirements.txt', 'message')
    assert commit.repo.git.commit.called is False


def test_apply_diff_apply_nothing_to_commit(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with a valid branch_name and valid diff_path and valid message
    WHEN commit is called with a valid message
    AND there are no diff changes
    THEN git.apply called
    AND index.commit not called
    """
    mock_repo.is_dirty.return_value = False
    commit = GitRepo('./', mock_repo)
    commit.repo.git.diff.return_value = []

    with patch('git.repo.fun.name_to_object'):
        commit.commit.apply_diff('test_branch', './requirements.txt', 'message')
    assert commit.repo.git.apply.called is True
    assert commit.repo.git.commit.called is False


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


def test_abort(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN abort is called
    THEN git.am called
    """
    commit = GitRepo('./', mock_repo)

    commit.commit.abort()
    assert commit.repo.git.am.called is True


def test_abort_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN abort is called
    AND the abort fails with an exception
    THEN an AbortException is raised
    """
    mock_repo.git.am.side_effect = git.GitCommandError('abort', '')
    commit = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.AbortException):
        commit.commit.abort()


def test_reverse(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN reverse is called with a valid diff_path
    THEN git.am called
    """
    commit = GitRepo('./', mock_repo)

    commit.commit.reverse('./requirements.txt')
    assert commit.repo.git.apply.called is True


def test_reverse_diff_file_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN reverse is called with and invalid diff_path
    THEN FileDoesntExistException raised
    AND git.apply not called
    """
    commit = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.FileDoesntExistException):
        commit.commit.reverse('./thisdoesntexist')
    assert commit.repo.git.apply.called is False


def test_reverse_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN reverse is called with a valid diff_path
    AND the reverse fails with an exception
    THEN an RevertException is raised
    """
    mock_repo.git.apply.side_effect = git.GitCommandError('apply', '')
    commit = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.RevertException):
        commit.commit.reverse('./requirements.txt')
