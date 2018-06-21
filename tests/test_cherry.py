#! /usr/bin/env python
"""Tests for GitWrapperCherry"""

from git_wrapper.cherry import GitWrapperCherry


def test_on_head_only_all_new(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN on_head_only method is called with no upstream equivalent changes
    THEN a dictionary is returned containing two sha1's and commits
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = '+ sha1 commit1\n+ sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha1': 'commit1', 'sha2': 'commit2', 'sha3': 'commit3'}
    assert expected == cherry.on_head_only('upstream', 'HEAD')


def test_on_head_only_with_mixed(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN on_head_only method is called with a mix of
         upstream equivalent and not equivalent changes
    THEN a dictionary is returned containing two sha1's and commits
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = '+ sha1 commit1\n- sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha1': 'commit1', 'sha3': 'commit3'}
    assert expected == cherry.on_head_only('upstream', 'HEAD')


def test_on_head_only_no_new(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN on_head_only method is called with a only upstream equivalent changes
    THEN an empty dictionary is returned
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = '- sha1 commit1\n- sha2 commit2\n- sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == cherry.on_head_only('upstream', 'HEAD')


def test_on_head_only_empty(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN on_head_only is called with no changes
    THEN an empty dictionary is returned
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = ''
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == cherry.on_head_only('upstream', 'HEAD')


def test_all_equivalent_changes(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN equivalent is called with only equivalent upstream/downstream changes.
    THEN a dictionary is returned with all changes
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = '- sha1 commit1\n- sha2 commit2\n- sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha1': 'commit1', 'sha2': 'commit2', 'sha3': 'commit3'}
    assert expected == cherry.equivalent('upstream', 'HEAD')


def test_equivalent_mixed_changes(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN equivalent is called with mix equivalent and HEAD changes.
    THEN a dictionary is returned with only the equivalent changes.
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = '+ sha1 commit1\n- sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    expected = {'sha2': 'commit2'}
    assert expected == cherry.equivalent('upstream', 'HEAD')


def test_equivalent_downstream_only(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN equivalent is called with mix HEAD only changes.
    THEN an empty dictionary is returned.
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = '+ sha1 commit1\n+ sha2 commit2\n+ sha3 commit3'
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == cherry.equivalent('upstream', 'HEAD')


def test_equivalent_no_changes(mock_repo):
    """
    GIVEN GitWrapperCherry initialized with a path and repo
    WHEN equivalent is called with no changes.
    THEN an empty dictionary is returned.
    """
    cherry = GitWrapperCherry('./', mock_repo)
    lines = ''
    attrs = {'cherry.return_value': lines}
    mock_repo.git.configure_mock(**attrs)
    assert {} == cherry.equivalent('upstream', 'HEAD')
