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


def test_apply_patch(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch_name and valid path
    THEN git.am is called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.branch.apply_patch('test_branch', './requirements.txt')
    assert repo.git.am.called is True


def test_apply_patch_wrong_branch_name(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with an invalid branch_name and valid path
    THEN ReferenceNotFoundExceptionRaised
    AND git.am not called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.branch.apply_patch('invalid_branch', './requirements.txt')
    assert repo.git.am.called is False


def test_apply_patch_not_a_file(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch_name and invalid path
    THEN FileDoesntExistException raised
    AND git.am not called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.FileDoesntExistException):
            repo.branch.apply_patch('test_branch', './git_wrapper')
    assert repo.git.am.called is False


def test_apply_patch_checkout_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch name and a valid path
    AND checkout fails with an exception
    THEN a CheckoutException is raised
    AND git.am not called
    """
    mock_repo.git.checkout.side_effect = git.GitCommandError('checkout', '')
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            repo.branch.apply_patch('test_branch', './requirements.txt')
    assert repo.git.am.called is False


def test_apply_patch_apply_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with a valid branch name and a valid path
    AND git.am fails with an exception
    THEN a ChangeNotAppliedException is raised
    """
    mock_repo.git.am.side_effect = git.GitCommandError('am', '')
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.ChangeNotAppliedException):
            repo.branch.apply_patch('test_branch', './requirements.txt')


def test_apply_diff(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with a valid branch_name and valid diff_path and valid message
    THEN index.commit is called
    """
    mock_repo.is_dirty.return_value = False
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.branch.apply_diff('test_branch', './requirements.txt', 'message', True)
    assert repo.git.apply.called is True
    assert repo.git.commit.called is True


def test_apply_diff_on_invalid_branch(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with an invalid branch_name and valid path
    THEN ReferenceNotFoundExceptionRaised
    AND git.apply not called
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.branch.apply_diff('invalid_branch', './requirements.txt', 'message')
    assert repo.git.apply.called is False


def test_apply_diff_on_dirty_workspace(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called on a dirty repository
    THEN a DirtyRepositoryException is raised
    AND git.apply not called
    """
    mock_repo.is_dirty.return_value = True
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.DirtyRepositoryException):
            repo.branch.apply_diff('test_branch', './requirements.txt', 'message')
    assert mock_repo.is_dirty.called is True
    assert repo.git.apply.called is False


def test_apply_diff_no_commit_message(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with valid branch_name, valid diff_path and invalid message
    THEN CommitMessageMissingException raised
    AND index.commit not called
    """
    mock_repo.is_dirty.return_value = False
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CommitMessageMissingException):
            repo.branch.apply_diff('test_branch', './requirements.txt', '')
    assert repo.git.commit.called is False


def test_apply_diff_not_a_file(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with valid parameters
    THEN FileDoesntExistException raised
    AND git.apply not called
    """
    mock_repo.is_dirty.return_value = False
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.FileDoesntExistException):
            repo.branch.apply_diff('test_branch', 'doesntexist.txt', 'message')
    assert repo.git.apply.called is False


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
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            repo.branch.apply_diff('invalid_branch', './requirements.txt', 'my message')
    assert repo.git.commit.called is False


def test_apply_diff_apply_fails(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_diff is called with a valid branch_name and valid diff_path and valid message
    AND git.apply fails with an exception
    THEN an ChangeNotAppliedException is raised
    """
    mock_repo.is_dirty.return_value = False
    mock_repo.git.apply.side_effect = git.GitCommandError('apply', '')
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.ChangeNotAppliedException):
            repo.branch.apply_diff('test_branch', './requirements.txt', 'message')
    assert repo.git.commit.called is False


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
    repo = GitRepo('./', mock_repo)
    repo.git.diff.return_value = []

    with patch('git.repo.fun.name_to_object'):
        repo.branch.apply_diff('test_branch', './requirements.txt', 'message')
    assert repo.git.apply.called is True
    assert repo.git.commit.called is False


def test_abort_patch_apply(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN abort_patch_apply is called
    THEN git.am called
    """
    repo = GitRepo('./', mock_repo)

    repo.branch.abort_patch_apply()
    assert repo.git.am.called is True


def test_abort_patch_apply_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN abort_patch_apply is called
    AND the abort_patch_apply fails with an exception
    THEN an Abort_Patch_ApplyException is raised
    """
    mock_repo.git.am.side_effect = git.GitCommandError('abort_patch_apply', '')
    repo = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.AbortException):
        repo.branch.abort_patch_apply()


def test_reverse_diff(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN reverse_diff is called with a valid diff_path
    THEN git.am called
    """
    repo = GitRepo('./', mock_repo)

    repo.branch.reverse_diff('./requirements.txt')
    assert repo.git.apply.called is True


def test_reverse_diff_diff_file_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN reverse_diff is called with and invalid diff_path
    THEN FileDoesntExistException raised
    AND git.apply not called
    """
    repo = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.FileDoesntExistException):
        repo.branch.reverse_diff('./thisdoesntexist')
    assert repo.git.apply.called is False


def test_reverse_diff_error(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN reverse_diff is called with a valid diff_path
    AND the reverse_diff fails with an exception
    THEN an RevertException is raised
    """
    mock_repo.git.apply.side_effect = git.GitCommandError('apply', '')
    repo = GitRepo('./', mock_repo)

    with pytest.raises(exceptions.RevertException):
        repo.branch.reverse_diff('./requirements.txt')


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
