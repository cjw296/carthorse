|CircleCI|_

.. |CircleCI| image:: https://circleci.com/gh/cjw296/carthorse/tree/master.svg?style=shield
.. _CircleCI: https://circleci.com/gh/cjw296/carthorse/tree/master

Carthorse
=========

Safely creating releases when you change the version number.

You use it by adding configuration to a yaml or toml file, and then adding the following
to your continuous integration pipeline::

    pip install -U carthorse
    carthorse

TOML Configuration
------------------

Your file should contain a section such as the following::

    [tool.carthorse]
    version-from = "poetry"
    tag-format = "v{version}"
    when = [
      "version-not-tagged"
    ]
    actions = [
       { run="poetry publish --username $POETRY_USER --password $POETRY_PASS --build"},
       { name="create-tag"},
    ]

This is designed so that it can be included as part of a ``pyproject.toml`` file.

YAML Configuration
------------------

Your file should contain a section such as the following::

    carthorse:
      version-from: poetry
      tag-format: v{version}
      when:
        - version-not-tagged
      actions:
        - run: "poetry publish --username $POETRY_USER --password $POETRY_PASS --build"
        - create-tag

What does it do?
----------------

Roughly speaking:

- Extract your project's version from its source code.
- Format a tag based on the version
- Perform a number of checks, if any of those fail, stop.
- Perform any actions you specify.

Version extraction
------------------

The following methods of extracting the version of a project are currently supported:

``setup.py``
  This will run ``python setup.py --version`` and use the version returned.

``poetry``
  This will parse a project's ``pyproject.toml`` and use the ``tool.poetry.version``
  key as the version for the project.

``flit``
  This will extract the version from a flit-style ``__version__`` without importing
  the package. For example, if your module is called ``foobar``, this will look in either
  ``foobar/__init__.py`` or ``foobar.py``. The config for that would be::

    [tool.carthorse]
    version-from = { name="flit", module="foobar" }

``path``
  This will extract the version from a specified file. By default, this will be the stripped
  contents of the whole file, but a pattern can be specified. This can be useful to extract
  the version from a ``setup.py`` without executing it. The config would that would be::

    [tool.carthorse]
    version-from = { name="path", path="setup.py", pattern="version='(?P<version>[^']+)" }

``none``
  This will return an empty string as the version. This is useful if you're
  using carthorse as a way of managing git tags or timestamped releases.

``env``
  This will extract the version from the specified environment variable. For example,
  if you have constructed the version in `$VERSION` you could extract it with::

    [tool.carthorse]
    version-from = { name="env"}

  If you need to extract it from an environment variable with a different name, for example
  `$MYVERSION`, you could extract it with::

    [tool.carthorse]
    version-from = { name="env", variable="MYVERSION" }

Tag formatting
--------------

The ``tag-format`` configuration option lets you control the format of the version tag
by specifying a python format string into which the version will be interpolated.
The default is ``v{version}``.

The names available to use in this are:

``version``
  The version returned by the version extraction.

``now``
  A python ``datetime`` for the current date and time.

Performing checks
-----------------

Each check in the ``when`` configuration section will be performed in order. If any fail
then no actions will be performed.

The following checks are currently available:

``version_not_tagged``
  This will pass if no current git tag exists for the version extracted from the poject.

``never``
  A safety net and testing helper, this check will never pass.

``always``
 Useful if you basically want to skip the checking phase.

Actions
-------

If all the checks pass, then the actions listed are executed in order. If an error occurs
during the execution of an action, no further actions will be executed.

The following actions are currently available:

``run``
  Run the specified command in a shell. The full environment will be passed through and
  ``$TAG`` will contain the tag computed from the tag format.

``create_tag``
  This will create a git tag for the computed tag based on the extracted version and push
  it to the specified remote. By default, the ``origin`` remote is used.

  If you are using carthorse to manage tags per environment, for example, you can for existing
  tags to be updated as follows::

    [tool.carthorse]
    ...
    actions = [
       { name="create-tag", update=true},
    ]

Changes
-------

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
