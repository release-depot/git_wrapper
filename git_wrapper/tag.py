#! /usr/bin/env python
"""This module acts as an interface for acting on git tags"""

import git
from future.utils import raise_from

from git_wrapper import exceptions
from git_wrapper.utils.decorators import reference_exists


class GitTag(object):

    def __init__(self, git_repo, logger):
        """Constructor for GitTag object

            :param repo.GitRepo git_repo: An already constructed GitRepo object
            :param logging.Logger logger: A pre-configured Python Logger object
        """
        self.git_repo = git_repo
        self.logger = logger

    @reference_exists('reference')
    def create(self, name, reference):
        """Create a new tag to the target reference.

           :param str name: New tag's name
           :param str reference: What the tag should point to
        """
        try:
            self.git_repo.repo.create_tag(name, reference)
        except git.GitCommandError as ex:
            msg = "Error creating tag {name} on {ref}. Error: {error}".format(
                name=name, ref=reference, error=ex
            )
            raise_from(exceptions.TaggingException(msg), ex)

    @reference_exists('name')
    def delete(self, name):
        """Delete tag from local repository

           :param str name: Tag name to delete
        """
        try:
            self.git_repo.git.tag("-d", name)
        except git.GitCommandError as ex:
            msg = "Error deleting tag {name}. Error: {error}".format(
                name=name, error=ex
            )
            raise_from(exceptions.TaggingException(msg), ex)

    @reference_exists('name')
    def push(self, name, remote, dry_run=False):
        """Push specified tag to specified remote

           :param str name: Tag name
           :param str remote: Remote to push the tag to
           :param bool dry_run: Whether to run the commands in dry-run mode
        """
        if remote not in self.git_repo.remote.names():
            msg = "No remote named {0}".format(remote)
            raise exceptions.ReferenceNotFoundException(msg)

        msg = (
            "Error pushing tag {name} (dry-run: {dry_run}) to remote "
            "{remote}.".format(name=name, remote=remote, dry_run=dry_run)
        )

        try:
            if dry_run:
                self.git_repo.git.push("-n", remote, name)
            else:
                self.git_repo.git.push(remote, name)
        except git.GitCommandError as ex:
            raise_from(exceptions.PushException(msg), ex)
