class DirtyRepositoryException(Exception):
    """Repository workspace is dirty."""
    pass


class ReferenceNotFoundException(Exception):
    """Reference (commit, tag, branch, ...) doesn't exist."""
    pass


class CheckoutException(Exception):
    """Error occurred while switching branch."""
    pass


class RebaseException(Exception):
    """Error occurred during a rebase."""
    pass


class AbortException(Exception):
    """Error occurred while attempting to abort a command."""
    pass
