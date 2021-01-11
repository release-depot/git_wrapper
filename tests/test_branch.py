#! /usr/bin/env python
"""Tests for GitBranch"""

from mock import ANY, Mock, patch

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
    THEN git.am is called with only one argument (path) and no options
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.branch.apply_patch('test_branch', './requirements.txt')
    assert repo.git.am.called is True
    # The path gets translated to a full path which will change on every
    # system so we only check there was one argument only, with no other flags
    repo.git.am.assert_called_with(ANY)


def test_apply_patch_with_brackets_preserved(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN apply_patch is called with valid parameters
    AND keep_square_brackets is set to True
    THEN git.am is called with the --keep-non-patch option
    """
    repo = GitRepo('./', mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.branch.apply_patch('test_branch', './requirements.txt', keep_square_brackets=True)
    assert repo.git.am.called is True
    repo.git.am.assert_called_with('--keep-non-patch', ANY)


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


def test_reset(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset is called
    THEN repo.head.reset is called
    """
    mock_remote = Mock()
    mock_repo.remote.return_value = mock_remote

    repo = GitRepo(repo=mock_repo)
    with patch('git.repo.fun.name_to_object'):
        repo.branch.hard_reset()

    assert mock_remote.fetch.called is True  # Sync is called
    assert mock_repo.head.reset.called is True  # Reset is called


def test_reset_remote_reference_not_found(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset is called
    AND the remote + branch reference doesn't exist
    THEN ReferenceNotFoundException is raised
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.branch.hard_reset(refresh=False, remote="doesntExist")

    assert mock_repo.head.reset.called is False


def test_reset_checkout_failure(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset is called
    AND git.checkout fails
    THEN CheckoutException is raised
    """
    mock_repo.git.checkout.side_effect = git.GitCommandError('checkout', '')
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            repo.branch.hard_reset(refresh=False)

    assert mock_repo.head.reset.called is False


def test_reset_reset_failure(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset is called
    AND git.reset fails
    THEN ResetException is raised
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        mock_repo.head.reset.side_effect = git.GitCommandError('reset', '')
        with pytest.raises(exceptions.ResetException):
            repo.branch.hard_reset(refresh=False)


def test_reset_to_ref_with_checkout(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset is called with checkout
    THEN repo.head.reset is called
    AND repo.checkout is called once
    """
    repo = GitRepo(repo=mock_repo)
    with patch('git.repo.fun.name_to_object'):
        repo.branch.hard_reset_to_ref("main", "origin/main", checkout=True)

    assert mock_repo.head.reset.called is True
    assert mock_repo.git.checkout.call_count == 1


def test_reset_to_ref_detached_head_with_checkout(mock_repo, monkeypatch):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset is called with checkout
    AND the current HEAD is detached
    THEN repo.head.reset is called
    AND repo.checkout is called once
    """
    class MockRef:
        @property
        def name(self):
            # Detached heads don't have a name
            raise TypeError

    repo = GitRepo(repo=mock_repo)
    with patch('git.repo.fun.name_to_object'):
        mock_repo.head.ref = MockRef()
        repo.branch.hard_reset_to_ref("main", "origin/main", checkout=True)

    assert mock_repo.head.reset.called is True
    assert mock_repo.git.checkout.call_count == 1


def test_reset_to_ref_without_checkout(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset_to_ref is called with checkout False
    THEN repo.head.reset is called
    AND repo.checkout is called twice to return to the original state
    """
    repo = GitRepo(repo=mock_repo)
    with patch('git.repo.fun.name_to_object'):
        repo.branch.hard_reset_to_ref("main", "origin/main", checkout=False)

    assert mock_repo.head.reset.called is True
    assert mock_repo.git.checkout.call_count == 2


def test_reset_to_ref_without_checkout_fails(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN reset_to_ref is called with checkout False
    AND switching back fails
    THEN checkoutException is raised
    """
    mock_repo.git.checkout.side_effect = [None, git.GitCommandError('checkout', '')]

    repo = GitRepo(repo=mock_repo)
    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.CheckoutException):
            repo.branch.hard_reset_to_ref("main", "origin/main", checkout=False)

    assert mock_repo.head.reset.called is True
    assert mock_repo.git.checkout.call_count == 2


def test_local_branch_exists(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.exists is called with a valid branch and None remote
    THEN True is returned
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.branches = ["master", "test"]

    assert repo.branch.exists("test") is True


def test_local_branch_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.exists is called with an invalid branch and None remote
    THEN False is returned
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.branches = ["master", "test"]

    assert repo.branch.exists("another-test") is False


def test_branch_exists_with_invalid_remote(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.exists is called with a valid branch and invalid remote
    THEN a RemoteException is raised
    """
    repo = GitRepo(repo=mock_repo)

    with pytest.raises(exceptions.RemoteException):
        assert repo.branch.exists("another", "doesntexist")


def test_remote_branch_exists(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.exists is called with a valid branch and valid remote
    THEN True is returned
    """
    repo = GitRepo(repo=mock_repo)

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="testremote", refs=["testbranch"])
    mock_repo.remotes.extend([remote])

    assert repo.branch.exists("testbranch", "testremote") is True


def test_remote_branch_doesnt_exists(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.exists is called with an invalid branch and valid remote
    THEN True is returned
    """
    repo = GitRepo(repo=mock_repo)

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="testremote", refs=[])
    mock_repo.remotes.extend([remote])

    assert repo.branch.exists("testbranch", "testremote") is False


def test_create_branch(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.create is called with a valid name and start_ref
    THEN git.branch is called
    AND git.checkout is not called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert repo.branch.create("test", "123456") is True
    repo.git.branch.assert_called_with("test", "123456")
    repo.git.checkout.assert_not_called()


def test_create_and_checkout_branch(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.create is called with valid parameters and checkout is True
    THEN git.branch is called
    AND git.checkout is called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert repo.branch.create("test", "123456", checkout=True) is True
    repo.git.branch.assert_called_with("test", "123456")
    repo.git.checkout.assert_called()


def test_create_branch_with_bad_start_ref(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.create is called with a valid name and invalid start_ref
    THEN a ReferenceNotFoundException is raised
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            assert repo.branch.create("test", "badref")


def test_create_branch_already_exists(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.create is called with a valid name and start_ref
    AND the branch already exists
    THEN git.branch is not called
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.branches = ["test", "master"]

    with patch('git.repo.fun.name_to_object'):
        repo.branch.create("test", "123456")
    assert repo.git.branch.called is False
    assert repo.git.checkout.called is False


def test_create_branch_already_exists_and_check_it_out(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.create is called with valid params and checkout is True
    AND the branch already exists
    THEN git.branch is not called
    AND git.checkout is called
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.branches = ["test", "master"]

    with patch('git.repo.fun.name_to_object'):
        repo.branch.create("test", "123456", checkout=True)
    assert repo.git.branch.called is False
    assert repo.git.checkout.called is True


def test_create_branch_already_exists_and_reset_it(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.create is called with a valid name and start_ref
    AND the branch already exists and reset_if_exists is True
    THEN hard_reset_to_ref is called
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.branches = ["test", "master"]

    mock_hard_reset = Mock()
    repo.branch.hard_reset_to_ref = mock_hard_reset

    with patch('git.repo.fun.name_to_object'):
        repo.branch.create("test", "123456", True)
    assert mock_hard_reset.called is True


def test_remote_contains_branch_not_found(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.remote_contains is called with an invalid branch name
    THEN a ReferenceNotFoundException is raised
    AND the exception message contains branch
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            mock_name_to_object.side_effect = git.exc.BadName()
            repo.branch.remote_contains('doesNotExist', '12345')
    assert 'branch' in str(exc_info.value)


def test_remote_contains_commit_not_found(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN branch.remote_contains is called with an invalid commit hash
    THEN a ReferenceNotFoundException is raised
    AND the exception message contains hash
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            # First name_to_object call is to check the branch, let it succeed
            def side_effect(mock, ref):
                if ref != "origin/mybranch":
                    raise git.exc.BadName
            mock_name_to_object.side_effect = side_effect
            repo.branch.remote_contains('origin/mybranch', 'doesNotExist')
    assert 'hash' in str(exc_info.value)


def test_remote_contains_with_commit_present(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.remote_contains is called with a valid branch and hash
    AND git_repo.git.branch returns data
    THEN branch.remote_contains returns True
    """
    remote_branch = "origin/mybranch"
    mock_repo.git.branch.return_value = remote_branch
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert repo.branch.remote_contains(remote_branch, '12345') is True


def test_remote_contains_with_commit_absent(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN branch.remote_contains is called with a valid branch and hash
    AND git_repo.git.branch returns empty string
    THEN branch.remote_contains returns True
    """
    mock_repo.git.branch.return_value = ""
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        assert repo.branch.remote_contains("origin/mybranch", '12345') is False
