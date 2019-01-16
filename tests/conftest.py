#! /usr/bin/env python
"""Base fixtures for unit tests"""

from collections import namedtuple
from datetime import datetime
from mock import Mock

import git
from git.util import IterableList
import pytest


@pytest.fixture
def mock_repo():
    """repo mock fixture"""
    repo_mock = Mock()
    repo_git_mock = Mock()
    repo_mock.attach_mock(repo_git_mock, 'git')

    remote = Mock(spec=git.Remote)
    remote.configure_mock(name="origin", url="http://example.com")
    remote_list = IterableList("name")
    remote_list.extend([remote])

    repo_mock.remotes = remote_list
    repo_mock.branches = []

    return repo_mock


@pytest.fixture
def fake_commits(count=3):
    """A few commit-like objects, to test log_diff functions"""
    Author = namedtuple("Author", ["name", "email"])
    Commit = namedtuple("Commit", ["hexsha", "message", "summary", "author",
                                   "authored_datetime"])

    commits = []
    for i in range(0, count):
        author = Author(name="Test Author", email="testauthor@example.com")
        msg = "This is a commit message (#{0})\nWith some details.".format(i)

        commit = Commit(
            hexsha="00{0}0000000000000000".format(i),
            message=msg,
            summary="This is a commit message (#{0})".format(i),
            author=author,
            authored_datetime=datetime(2018, 12, 5, 10, 36, 19)
        )
        commits.append(commit)

    return commits
