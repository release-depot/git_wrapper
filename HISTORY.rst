=======
History
=======

0.0.1 (2018-06-25)
------------------

* First release on PyPI.

0.1.0 (2018-07-05)
------------------

* Second release on PyPI.
* Base functionality
* git cherry support
* Removing pipenv support.

0.2.0 (2019-01-18)
------------------

* Third release on PyPI.
* Major refactor to better align the data model.
* Added several new features
        * Log diff generation
        * Improved clone support including bare repos and destroy/reclone
        * Revert support
        * Support for rebasing to a branch or commit.

0.2.1 (2019-04-15)
------------------

* Fourth release on PyPI.
* Added several new features
        * Add function to compare commit references
        * Add tagging functions

0.2.2 (2020-07-20)
------------------

* Fifth release on PyPI.
* Added new function to check if a commit exists on a given remote branch

0.2.3 (2020-12-15)
------------------

* Added checkout parameter to branch creation and hard reset functions


0.2.4 (2021-01-11)
------------------

* Added new function to cherry-pick a given commit
* New parameter added to apply_patch() to preserve square brackets in commit messages
* Added new function to grep logs
* Deprecated location of other log functions in GitBranch, they should now be called from GitLog

0.2.5 (2021-01-12)
------------------

* Fix RST formatting issue to unbreak Pypi uploads
