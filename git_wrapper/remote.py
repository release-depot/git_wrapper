#! /usr/bin/env python
"""This module acts as an interface for acting on git remotes"""

import git


class GitRemote(object):

    def __init__(self, git_repo, logger):
        """Constructor for GitRemote object

            :param repo.GitRepo git_repo: An already constructed GitRepo object to use
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.git_repo = git_repo
        self.logger = logger

    def names(self):
        """Returns a list of remotes for a given repo

            :return list: A list of utf-8 encoded remote names
        """
        return [x.name for x in self.git_repo.repo.remotes]

    def add(self, name, url):
        """Adds a remote to the given repo

            :param str name: The name for the remote
            :param str url: The url to use for the remote
            :return bool: True if the remote was added, False otherwise
        """
        self.logger.debug("Adding remote %s (%s) to repo %s", name, url, self.git_repo.repo.working_dir)
        ret_status = False

        try:
            remote = self.git_repo.repo.create_remote(name, url)
        except git.CommandError as ex:
            self.logger.debug("Failed to create new remote %s (%s). Error: %s", name, url, ex)
            return ret_status

        try:
            remote.update()
            ret_status = True
        except git.CommandError as ex:
            self.logger.debug("Failed to update new remote %s (%s), removing it. Error: %s", name, url, ex)
            self.git_repo.repo.delete_remote(remote)

        return ret_status
