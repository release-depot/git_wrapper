===========
git_wrapper
===========


.. image:: https://img.shields.io/pypi/v/git_wrapper.svg
        :target: https://pypi.python.org/pypi/git_wrapper

.. image:: https://img.shields.io/travis/release-depot/git_wrapper.svg
        :target: https://travis-ci.org/release-depot/git_wrapper

.. image:: https://readthedocs.org/projects/git-wrapper/badge/?version=latest
        :target: https://git-wrapper.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python wrapper around GitPython


* Free software: MIT license
* Documentation: https://git-wrapper.readthedocs.io.


Features
--------

* TODO

Development
-----------

There are several dependencies needed to build and work on git_wrapper.  Using
your distribution's package manager, install these system packages::

  GitPython

git_wrapper uses the upcoming standard of Pipfiles via pipenv.  This is integrated
into our Makefile and once you have the above dependencies, you can simply run::

  make dev

This will install our dev environment for the package via pipenv.  It is installed
with --user, so it does not affect your site-packages.  Pipenv creates a unique virtualenv
for us, which you can activate via::

  pipenv shell

See the `pipenv documentation <https://docs.pipenv.org/>`_ for more detail.

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

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
