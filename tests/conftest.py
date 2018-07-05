#! /usr/bin/env python
"""Base fixtures for unit tests"""

from mock import Mock

import pytest


@pytest.fixture
def mock_repo():
    """repo mock fixture"""
    repo_mock = Mock()
    repo_git_mock = Mock()
    repo_mock.attach_mock(repo_git_mock, 'git')
    return repo_mock


def obj_generator(names):
    '''Generates objects to be used with git.Repo.branches, remotes calls'''
    ret_data = {}
    for name in names:
        obj = Mock()
        obj.name = name
        ret_data[name] = obj

    return ret_data


@pytest.fixture
def mock_repo_with_branches():
    repo_mock = mock_repo()

    # Set up the local branches
    branches = ['branchA', 'branchB']
    attrs = {'branches': obj_generator(branches)}
    repo_mock.configure_mock(**attrs)

    # Set up remotes
    remotes = ['origin', 'remoteA']
    attrs = {'remotes': obj_generator(remotes)}
    repo_mock.configure_mock(**attrs)

    # Set up the remote branches (as references)
    remote_refs = ['master', 'branchC', 'test/branch-with-slashes']
    attrs = {'refs': obj_generator(remote_refs)}
    repo_mock.remotes['remoteA'].configure_mock(**attrs)

    return repo_mock
