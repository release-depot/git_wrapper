#! /usr/bin/env python
"""This module acts as an interface for acting on git tags"""

import git

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
            msg = f"Error creating tag {name} on {reference}. Error: {ex}"
            raise exceptions.TaggingException(msg) from ex

    @reference_exists('name')
    def delete(self, name):
        """Delete tag from local repository

           :param str name: Tag name to delete
        """
        try:
            self.git_repo.git.tag("-d", name)
        except git.GitCommandError as ex:
            msg = f"Error deleting tag {name}. Error: {ex}"
            raise exceptions.TaggingException(msg) from ex

    @reference_exists('name')
    def push(self, name, remote, dry_run=False):
        """Push specified tag to specified remote

           :param str name: Tag name
           :param str remote: Remote to push the tag to
           :param bool dry_run: Whether to run the commands in dry-run mode
        """
        if remote not in self.git_repo.remote.names():
            msg = f"No remote named {remote}"
            raise exceptions.ReferenceNotFoundException(msg)

        msg = (f"Error pushing tag {name} (dry-run: {dry_run}) to remote "
               f"{remote}.")

        try:
            if dry_run:
                self.git_repo.git.push("-n", remote, name)
            else:
                self.git_repo.git.push(remote, name)
        except git.GitCommandError as ex:
            raise exceptions.PushException(msg) from ex

    def names(self):
        """List git tags in the repository."""
        try:
            tags_list = [x.name for x in self.git_repo.repo.tags]
        except git.GitCommandError as ex:
            repo_path = self.git_repo.repo.working_dir
            msg = f"Error listing tags for {repo_path}. Error: {ex}"
            raise exceptions.TaggingException(msg) from ex

        return tags_list
