#! /usr/bin/env python
"""This module acts as an interface for common git tasks"""

import logging

import git
from future.utils import raise_from

from git_wrapper import exceptions
from git_wrapper.remote import GitRemote


class GitRepo(object):
    """Provides a wrapper to interact with a git repository"""

    def __init__(self, path='', repo=None, logger=None):
        """Constructor for GitRepo object
            :param str path: Path to a git repo Default('')
            :param git.Repo repo: An already constructed git.Repo object to use Default(None)
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.__repo = None  # Added to clear pylint warnings
        self.__setup(path, repo)
        self._setup_logger(logger)

    def _setup_logger(self, logger):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self._remote = None

    def __setup(self, path, repo):
        """Sets the path and repo after performing validation

            :param str path: Path to a directory containing a git repository
            :param git.Repo repo: An already constructed git.Repo object to use
        """
        if repo is not None:
            self.repo = repo
        elif path != '':
            self.repo = git.Repo(path)
        else:
            raise Exception('No path or repo given')

    @property
    def repo(self):
        """Returns the git repo for a given path

            :return git.Repo: A reference to the internal git.Repo object
        """
        return self.__repo

    @repo.setter
    def repo(self, new_repo):
        """Allows for use of an already constructed repo

            :param git.Repo new_repo: An already constructed git.Repo object to use
        """
        self.__repo = new_repo

    @property
    def git(self):
        """Returns the git command for a given repo"""
        return self.repo.git

    def describe(self, sha):
        """Return tag and commit info for a given sha

           :param str sha: The SHA1 of the commit to describe
           :return dict: A dict with tag and patch data
        """
        ret_data = {'tag': '', 'patch': ''}
        try:
            output = self.git.describe('--all', sha).split('-g')
        except git.CommandError as ex:
            msg = "Error while running describe command on sha {sha}: {error}".format(sha=sha, error=ex)
            raise_from(exceptions.DescribeException(msg), ex)

        if output:
            tag = output[0]
            # Lightweight tags have a tag/ prefix when returned
            if tag.startswith('tag/'):
                tag = tag[4:]
            ret_data['tag'] = tag
            if len(output) > 1:
                ret_data['patch'] = output[1]
        return ret_data

    @property
    def remote(self):
        """Return object to act on the repo's remotes"""
        if not self._remote:
            self._remote = GitRemote(git_repo=self, logger=self.logger)
        return self._remote

    @remote.setter
    def remote(self, new_remote):
        """Set up object to interact with Remotes

            :param git_wrapper.remote.GitRemote new_remote: An already constructed GitRemote object to use
        """
        if not isinstance(new_remote, GitRemote):
            raise TypeError("Remote must be a GitRemote object.")
        self._remote = new_remote
