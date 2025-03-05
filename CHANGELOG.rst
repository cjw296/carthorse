Changes
=======

2.0.0 (5 Mar 2025)
~~~~~~~~~~~~~~~~~~

- Officially support Python 3.12 and Python 3.13

- Drop support for Python 3.11 and earlier.

- Add ``pyproject`` as a ``version-from``.

- Add ``update-major-tag`` action.

1.4.0 (4 Oct 2022)
~~~~~~~~~~~~~~~~~~

- Fix documentation bugs.

- Implement ``carthorse --dry-run``.

1.3.0 (4 Feb 2020)
~~~~~~~~~~~~~~~~~~

Changes such that carthorse can cover the same use cases as `ansible-role-createtag`__ without
needing ansible.

__ https://github.com/cjw296/ansible-role-createtag

- Added ``when`` of ``always``.

- Added skipping of version extraction using ``none``.

- Support extracting the project version from an environment variable.

- Make the current datetime available when building the tag.

- Add support for updating existing git tags.

1.2.0 (12 Sep 2019)
~~~~~~~~~~~~~~~~~~~

- Support extracting the project version from `flit`__-style project.

  __ https://flit.readthedocs.io/en/latest/index.html

- Support extracting the project version from a file, or part of a file by regex.

1.1.0 (1 Mar 2019)
~~~~~~~~~~~~~~~~~~

- Support extracting the project version from a ``setup.py``.

- Support for other packages providing ``version-from``, ``when`` and ``actions`` callables.

1.0.1 (27 Feb 2019)
~~~~~~~~~~~~~~~~~~~

- Better PyPI metadata.

1.0.0 (27 Feb 2019)
~~~~~~~~~~~~~~~~~~~

- First release, supporting poetry and git tagging.
