#! /usr/bin/env python
"""Base fixtures for unit tests"""

from mock import Mock

import git
import pytest


@pytest.fixture
def mock_repo():
    """repo mock fixture"""
    repo_mock = Mock()
    repo_git_mock = Mock()
    repo_mock.attach_mock(repo_git_mock, 'git')

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="origin", url="http://example.com")
    repo_mock.remotes = [remote]

    return repo_mock
