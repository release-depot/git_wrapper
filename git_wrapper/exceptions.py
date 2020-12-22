class GitWrapperException(Exception):
    """Superclass for this library's exceptions"""
    pass


class DirtyRepositoryException(GitWrapperException):
    """Repository workspace is dirty."""
    pass


class ReferenceNotFoundException(GitWrapperException):
    """Reference (commit, tag, branch, ...) doesn't exist."""
    pass


class CheckoutException(GitWrapperException):
    """Error occurred while switching branch."""
    pass


class RebaseException(GitWrapperException):
    """Error occurred during a rebase."""
    pass


class AbortException(GitWrapperException):
    """Error occurred while attempting to abort a command."""
    pass


class RevertException(GitWrapperException):
    """Error occurred while attempting to perform a revert."""
    pass


class DescribeException(GitWrapperException):
    """Error occurred while running the describe command."""
    pass


class CommitMessageMissingException(GitWrapperException):
    """Cannot create a commit without a commit message."""
    pass


class ChangeNotAppliedException(GitWrapperException):
    """Error occurred while applying a changeset onto a repo."""
    pass


class FileDoesntExistException(GitWrapperException):
    """File doesn't exist."""
    pass


class RepoCreationException(GitWrapperException):
    """Error occurred while creating or cloning a repo."""
    pass


class RemoteException(GitWrapperException):
    """Error occurred while doing an operation on a remote."""
    pass


class ResetException(GitWrapperException):
    """Error occurred while resetting."""
    pass


class TaggingException(GitWrapperException):
    """Error occurred while performing operation on tag."""
    pass


class PushException(GitWrapperException):
    """Error occurred while pushing to remote."""
    pass
