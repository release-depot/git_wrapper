#! /usr/bin/env python
"""Tests for GitRepo"""

from mock import Mock, patch
import shutil

import git
import pytest

from git_wrapper import exceptions
from git_wrapper.remote import GitRemote
from git_wrapper.repo import GitRepo


def test_repo(mock_repo):
    """
    GIVEN GitRepo initialized with a path and no repo object
    WHEN the object is created
    THEN a repo added
    """
    with patch('git_wrapper.repo.git') as git_mock:
        attrs = {'Repo.return_value': mock_repo}
        git_mock.configure_mock(**attrs)
        git_util = GitRepo('./')
        assert mock_repo == git_util.repo


def test_not_path_no_repo():
    """
    GIVEN GitRepo initialized with no path or repo object
    WHEN the object is created
    THEN an exception is raised
    """
    with pytest.raises(Exception):
        GitRepo('', None)


def test_git_command(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN the git property is called
    THEN a git object is returned
    """
    git_util = GitRepo('./', mock_repo)

    assert mock_repo.git is git_util.git


def test_describe_tag_and_patch(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN describe is called with a tag and patch value
    THEN a dictionary with tag and patch keys is returned
    """
    expected = {'tag': '1.0.0', 'patch': '12345'}
    attrs = {'describe.return_value': '1.0.0-g12345'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_tag_only(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called a tag value only
    THEN a dictionary with a tag and empty patch is returned
    """
    expected = {'tag': '1.0.0', 'patch': ''}
    attrs = {'describe.return_value': '1.0.0'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_empty(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called with a bad hash
    THEN a dictionary with an empty tag and patch is returned
    """
    expected = {'tag': '', 'patch': ''}
    attrs = {'describe.return_value': ''}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_describe_sha_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called with a non-existent hash
    THEN a ReferenceNotFoundException is raised
    """
    git_util = GitRepo('./', mock_repo)
    git_util.git.describe.side_effect = git.CommandError('describe')

    with pytest.raises(exceptions.DescribeException):
        git_util.describe('12345')


def test_describe_with_lightweight_tags(mock_repo):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN describe is called with a good hash for a lightweight tag
    THEN a dictionary with a tag and empty patch is returned
    AND the tag/ prefix is stripped from the tag
    """
    expected = {'tag': '1.0.0-lw', 'patch': ''}
    attrs = {'describe.return_value': 'tag/1.0.0-lw'}
    mock_repo.git.configure_mock(**attrs)

    git_util = GitRepo('./', mock_repo)

    assert expected == git_util.describe('12345')


def test_remote_setter(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the remote setter is called
    THEN the remote is set as expected
    """
    repo = GitRepo('./', mock_repo)
    new_remote = GitRemote(git_repo=repo, logger=None)
    repo.remote = new_remote
    assert repo.remote == new_remote


def test_remote_setter_wrong_type(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN the remote setter is called with the wrong type
    THEN a TypeError is raised
    """
    repo = GitRepo('./', mock_repo)
    with pytest.raises(TypeError):
        repo.remote = repo


def test_clone():
    """
    GIVEN GitRepo without a path or repo
    WHEN clone is called with a valid clone_from URL and clone_to path
    THEN Repo.clone_from is called
    """
    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone = GitRepo.clone('./', './testclone')
        assert mock_clone.called is True
        assert isinstance(clone, GitRepo)


def test_clone_failed():
    """
    GIVEN GitRepo without a path or repo
    WHEN clone is called with a valid clone_from URL and clone_to path
    AND Repo.clone_from fails with an exception
    THEN a RepoCreationException is raised
    """
    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        mock_clone.side_effect = git.GitCommandError('clone', '')
        with pytest.raises(exceptions.RepoCreationException):
            GitRepo.clone('./', './testclone')


def test_destroy_and_reclone(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    THEN Repo.clone_from is called
    WITH the expected remote url and local working dir
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        assert mock_clone.called_with('http://example.com', local_dir)


def test_destroy_no_path_no_repo(monkeypatch):
    """
    GIVEN GitRepo initialized with no path or repo object
    WHEN destroy_and_reclone is called
    THEN an exception is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    with pytest.raises(Exception):
        clone = GitRepo('', None)
        clone.destroy_and_reclone()


def test_destroy_no_remotes(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo does not have any remotes configured
    THEN an exception is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)

    with pytest.raises(exceptions.RepoCreationException):
        clone.repo.remotes = {}
        clone.destroy_and_reclone()


def test_destroy_no_remote_named_origin(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo does not have a remote named origin
    THEN Repo.clone_from is called
    WITH the remote url and local working dir from another remote
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697667fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="onlyremote", url="http://example.com/another")
    clone.repo.remotes = [remote]

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com/another', local_dir)


def test_destroy_and_multiple_remotes(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo has multiple remotes
    THEN Repo.clone_from is called
    AND create_remote is called
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="otherremote", url="http://example.com/another")
    clone.repo.remotes.append(remote)

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        new_repo_mock = Mock()
        mock_clone.return_value = new_repo_mock
        clone.destroy_and_reclone()
        assert mock_clone.called is True
        mock_clone.assert_called_with('http://example.com', local_dir)
        new_repo_mock.create_remote.assert_called_with(
            "otherremote",
            "http://example.com/another"
        )


def test_destroy_and_remote_creation_fails(mock_repo, monkeypatch):
    """
    GIVEN GitRepo initialized with a path and repo
    WHEN destroy_and_reclone is called
    AND the repo has several remotes
    AND create_remote fails
    THEN a RemoteException is raised
    """
    monkeypatch.setattr(shutil, 'rmtree', Mock())
    clone = GitRepo(repo=mock_repo)
    local_dir = '/tmp/8f697668fgitwrappertest'
    clone.repo.working_dir = local_dir

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="otherremote", url="http://example.com/another")
    clone.repo.remotes.append(remote)

    with patch('git.repo.base.Repo.clone_from') as mock_clone:
        new_repo_mock = Mock()
        mock_clone.return_value = new_repo_mock
        with pytest.raises(exceptions.RemoteException):
            new_repo_mock.create_remote.side_effect = git.GitCommandError('remote', '')
            clone.destroy_and_reclone()
        assert mock_clone.called is True
