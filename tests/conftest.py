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
