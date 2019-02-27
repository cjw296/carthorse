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

``poetry``
  This will parse a project's ``pyproject.toml`` and use the ``tool.poetry.version``
  key as the version for the project.

Tag formatting
--------------

The ``tag-format`` configuration option lets you control the format of the version tag
by specifying a python format string into which the version will be interpolated.
The default is ``v{version}``.

Performing checks
-----------------

Each check in the ``when`` configuration section will be performed in order. If any fail
then no actions will be performed.

The following checks are currently available:

``version_not_tagged``
  This will pass if no current git tag exists for the version extracted from the poject.

``never``
  A safety net and testing helper, this check will never pass.

Actions
-------

If all the checks pass, then the actions listed are executed in order. If an error occurs
during the execution of an action, no further actions will be executed.

The following actions are currently available:

``run``
  The the specified command in a shell. The full environment will be passed through and
  ``$TAG`` will contain the tag computed from the tag format.

``create_tag``
  This will create a git tag for the computed tag based on the extracted version and push
  it to the specified remote. By default, the ``origin`` remote is used.

1.0.0 (27 Feb 2019)
-------------------

- First release, supporting poetry and git tagging.
