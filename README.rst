===========
git_wrapper
===========


.. image:: https://img.shields.io/pypi/v/git_wrapper.svg
        :target: https://pypi.python.org/pypi/git_wrapper

.. image:: https://readthedocs.org/projects/git-wrapper/badge/?version=latest
        :target: https://git-wrapper.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Python wrapper around GitPython


* Free software: MIT license
* Documentation: https://git-wrapper.readthedocs.io.


Features
--------

See `documentation`_.

.. _`documentation`: https://git-wrapper.readthedocs.io/en/latest/source/modules.html


Notes
-----

This library only supports python 3. Some features may still work with python 2.7 but not all of the
syntax and features may be compatible.

Development
-----------

See CONTRIBUTING.rst.

Documentation
*************

To build the documentation on your checkout, simply run::

  make docs

We plan to get this published in the near future, and this README will be
updated when that happens.

Contributions
*************

All new code should include tests that excercise the code and prove that it
works, or fixes the bug you are trying to fix.  Any Pull Request without tests
will not be accepted.

Pushing a new release
*********************

1. Prepare a patch to update the version number (`example`_)
2. Once that's merged, tag that patch and push the new tag to the repo
3. Github Actions will then automatically build and publish a new release.


.. _example: https://github.com/release-depot/git_wrapper/commit/fc88bcb3158187ba9566dad896e3c688d8bc5109

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
