#! /usr/bin/env python
"""Tests for GitTag"""

from mock import patch

import git
import pytest

from git_wrapper import exceptions
from git_wrapper.repo import GitRepo


def test_create_tag(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.create is called with a valid name and reference
    THEN git.create_tag is called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.tag.create("my_tag", "123456")
    repo.repo.create_tag.assert_called_with("my_tag", "123456")


def test_create_tag_with_wrong_ref(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.create is called with a name and invalid reference
    THEN a ReferenceNotFoundException is raised
    AND git.create_tag is not called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.tag.create("my_tag", "123456")
    repo.repo.create_tag.assert_not_called()


def test_create_tag_failed(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.create is called with a valid name and reference
    AND git.create_tag fails
    THEN a TaggingException is raised
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.create_tag.side_effect = git.GitCommandError('create_tag', '')

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.TaggingException):
            repo.tag.create("my_tag", "123456")


def test_delete_tag(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.delete is called with a valid tag name
    THEN git.tag is called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.tag.delete("my_tag")
    repo.git.tag.assert_called_with("-d", "my_tag")


def test_delete_tag_that_doesnt_exist(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.delete is called with an invalid tag name
    THEN a ReferenceNotFoundException is raised
    AND git.tag is not called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object') as mock_name_to_object:
        mock_name_to_object.side_effect = git.exc.BadName()
        with pytest.raises(exceptions.ReferenceNotFoundException):
            repo.tag.delete("bad_tag")
    repo.git.tag.assert_not_called()


def test_delete_tag_failed(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.delete is called with a valid tag name
    AND git.tag fails
    THEN a TaggingException is raised
    """
    repo = GitRepo(repo=mock_repo)
    mock_repo.git.tag.side_effect = git.GitCommandError('delete_tag', '')

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.TaggingException):
            repo.tag.delete("my_tag")


def test_push_tag(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.push is called with a valid tag name and remote
    THEN git.push is called
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.tag.push("my_tag", "origin")
    repo.git.push.assert_called_with("origin", "my_tag")


def test_push_tag_as_dry_run(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.push is called with a valid tag name and remote
    AND dry_run is set to true
    THEN git.push is called with -n as first argument
    """
    repo = GitRepo(repo=mock_repo)

    with patch('git.repo.fun.name_to_object'):
        repo.tag.push("my_tag", "origin", True)
    repo.git.push.assert_called_with("-n", "origin", "my_tag")


def test_push_tag_to_bad_remote(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.push is called with a tag name and invalid remote
    THEN a ReferenceNotFoundException is raised
    AND git.push is not called
    """
    repo = GitRepo(repo=mock_repo)

    with patch("git.repo.fun.name_to_object"):
        with pytest.raises(exceptions.ReferenceNotFoundException) as exc_info:
            repo.tag.push("my_tag", "bad_remote")

    assert 'bad_remote' in str(exc_info.value)
    repo.git.push.assert_not_called()


def test_push_tag_failed(mock_repo):
    """
    GIVEN GitRepo is initialized with a path and repo
    WHEN tag.push is called with a valid tag name and remote
    AND git.push fails
    THEN a PushException is raised
    """
    repo = GitRepo(repo=mock_repo)
    repo.git.push.side_effect = git.GitCommandError('push', '')

    with patch('git.repo.fun.name_to_object'):
        with pytest.raises(exceptions.PushException):
            repo.tag.push("my_tag", "origin")
