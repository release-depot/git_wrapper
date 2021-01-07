#! /usr/bin/env python
"""This module acts as an interface for common git tasks"""

import logging
import os
import shutil

import git
from future.utils import raise_from

from git_wrapper.branch import GitBranch
from git_wrapper.commit import GitCommit
from git_wrapper import exceptions
from git_wrapper.log import GitLog
from git_wrapper.remote import GitRemote
from git_wrapper.tag import GitTag


class GitRepo(object):
    """Provides a wrapper to interact with a git repository"""

    def __init__(self, path='', repo=None, logger=None):
        """Constructor for GitRepo object

            :param str path: Path to a git repo Default('')
            :param git.Repo repo: An already constructed git.Repo object to use Default(None)
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.__repo = None  # Added to clear pylint warnings
        self._branch = None
        self._commit = None
        self._log = None
        self._remote = None
        self._tag = None

        self.__setup(path, repo)
        self._setup_logger(logger)

    def _setup_logger(self, logger):
        """Set up a pre-configured logger or create a new one

            :param logging.Logger logger: A pre-configured Python Logger object
        """
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

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

    @staticmethod
    def clone(clone_from, clone_to, bare=False):
        """Clone a repository.

           :param str clone_from: The url or path to clone the repo from
           :param str clone_to: The local path to clone to
           :param bool bare: Whether to create a bare repo
           :return GitRepo: Returns the newly created repo object
        """
        clone_to = os.path.realpath(os.path.expanduser(clone_to))
        logging.debug("Preparing to clone repository %s into directory %s",
                      clone_from, clone_to)

        try:
            repo = git.repo.base.Repo.clone_from(clone_from,
                                                 clone_to,
                                                 bare=bare)
        except git.GitCommandError as ex:
            msg = "Error cloning repository {repo}".format(repo=clone_from)
            raise_from(exceptions.RepoCreationException(msg), ex)

        return GitRepo(repo=repo)

    def destroy_and_reclone(self):
        """Deletes the current directory and reclone the repository."""
        # Get local path for the repo
        local_path = self.repo.working_dir

        self.logger.info("Preparing to delete and reclone repo %s", local_path)

        # Get all of the remotes info
        remotes = {}
        for r in self.repo.remotes:
            remotes[r.name] = r.url

        self.logger.debug("Remotes for %s: %s", local_path, ' '.join(list(remotes)))

        if len(remotes) == 0:
            msg = "No remotes found for repo {repo}, cannot reclone. Aborting deletion.".format(repo=local_path)
            raise exceptions.RepoCreationException(msg)

        # Select a remote for the clone, 'origin' by default
        if "origin" in remotes.keys():
            default_remote = "origin"
        else:
            default_remote = list(remotes)[0]

        self.logger.debug("Default remote for cloning set to '%s'", default_remote)

        # Delete the local repo
        self.logger.info("Deleting local repo at %s", local_path)
        shutil.rmtree(local_path, ignore_errors=True)

        # Clone it again
        repo = self.clone(remotes[default_remote], local_path)
        self.__setup(repo=repo.repo, path=local_path)

        # Recreate the remotes
        for name, url in remotes.items():
            if name != default_remote:
                try:
                    self.logger.debug("Adding remote %s", name)
                    r = self.repo.create_remote(name, url)
                except git.GitCommandError as ex:
                    msg = "Issue with recreating remote {remote}. Error: {error}".format(remote=name, error=ex)
                    raise_from(exceptions.RemoteException(msg), ex)

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

    @property
    def branch(self):
        """Return object to act on the repo's branches"""
        if not self._branch:
            self._branch = GitBranch(git_repo=self, logger=self.logger)
        return self._branch

    @branch.setter
    def branch(self, new_branch):
        """Set up object to interact with Branches

            :param git_wrapper.branch.GitBranch new_branch: An already constructed GitBranch object to use
        """
        if not isinstance(new_branch, GitBranch):
            raise TypeError("Branch must be a GitBranch object.")
        self._branch = new_branch

    @property
    def commit(self):
        """Return object to act on the repo's commits"""
        if not self._commit:
            self._commit = GitCommit(git_repo=self, logger=self.logger)
        return self._commit

    @commit.setter
    def commit(self, new_commit):
        """Set up object to interact with Commits

            :param git_wrapper.commit.GitCommit new_commit: An already constructed GitCommit object to use
        """
        if not isinstance(new_commit, GitCommit):
            raise TypeError("Commit must be a GitCommit object.")
        self._commit = new_commit

    @property
    def tag(self):
        """Return object to act on the repo's tags"""
        if not self._tag:
            self._tag = GitTag(git_repo=self, logger=self.logger)
        return self._tag

    @tag.setter
    def tag(self, new_tag):
        """Set up object to interact with Tags

            :param git_wrapper.tag.GitTag new_tag: Pre-constructed GitTag object
        """
        if not isinstance(new_tag, GitTag):
            raise TypeError("Tag must be a GitTag object.")
        self._tag = new_tag

    @property
    def log(self):
        """Return object to act on the repo's logs"""
        if not self._log:
            self._log = GitLog(git_repo=self, logger=self.logger)
        return self._log

    @log.setter
    def log(self, new_log):
        """Set up object to interact with Logs

            :param git_wrapper.log.GitLog new_log: Pre-constructed GitLog object
        """
        if not isinstance(new_log, GitLog):
            raise TypeError("Log must be a GitLog object.")
        self._log = new_log
