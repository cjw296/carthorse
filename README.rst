|CircleCI|_

.. |CircleCI| image:: https://circleci.com/gh/cjw296/carthorse/tree/master.svg?style=shield
.. _CircleCI: https://circleci.com/gh/cjw296/carthorse/tree/master

Carthorse
=========

Safely creating releases when you change the version number.

The intention is to only create the release tag when the release is good to go.
No more brown bag releases, where a tag is cut only to find there's a continuous integration
or build failure that means you immediately need to cut another tag.

You use it by adding configuration to a yaml or toml file, and then adding the following
to your continuous integration pipeline:

.. code-block:: bash

    pip install -U carthorse
    carthorse

What does it do?
----------------

- Extract your project's version from its source code.
- Format a tag based on the version.
- Perform a number of checks, if any of those fail, stop.
- Perform any actions you specify, which usually includes creating and pushing the version tag.

TOML Configuration
------------------

Your file should contain a section such as the following:

.. code-block:: toml

    [tool.carthorse]
    version-from = "poetry"
    tag-format = "v{version}"
    when = [
      "version-not-tagged"
    ]
    actions = [
       { run="poetry publish --build"},
       { name="create-tag"},
    ]

.. invisible-code-block: python

    run_config(
        expected_runs=['poetry publish --build'],
        expected_phrases=['git push origin tag v1.0']
    )

This is designed so that it can be included as part of a ``pyproject.toml`` file.

YAML Configuration
------------------

Your file should contain a section such as the following:

.. code-block:: yaml

    carthorse:
      version-from: poetry
      tag-format: v{version}
      when:
        - version-not-tagged
      actions:
        - run: "poetry publish --build"
        - create-tag

.. invisible-code-block: python

    run_config(
        expected_runs=['poetry publish --build'],
        expected_phrases=['git push origin tag v1.0']
    )

Version extraction
------------------

The following methods of extracting the version of a project are currently supported:

``pyproject.toml``
  This will parse a project's ``pyproject.toml`` and use the standard `version`__
  key as the version for the project.

  __  https://packaging.python.org/en/latest/specifications/pyproject-toml/#version

``setup.py``
  This will run ``python setup.py --version`` and use the version returned.

``poetry``
  This will parse a project's ``pyproject.toml`` and use the ``tool.poetry.version``
  key as the version for the project.

``flit``
  This will extract the version from a flit-style ``__version__`` without importing
  the package. For example, if your module is called ``foobar``, this will look in either
  ``foobar/__init__.py`` or ``foobar.py``. The config for that would be:

  .. code-block:: toml

    [tool.carthorse]
    version-from = { name="flit", module="foobar" }

  .. invisible-code-block: python

      run_config(expected_runs=['echo v2.0'])

``file``
  This will extract the version from a specified file. By default, this will be the stripped
  contents of the whole file, but a pattern can be specified. This can be useful to extract
  the version from a ``setup.py`` without executing it. The config for that would be:

  .. code-block:: toml

    [tool.carthorse]
    version-from = { name="file", path="setup.py", pattern="version=['\"](?P<version>[^'\"]+)" }

  .. invisible-code-block: python

      run_config(expected_runs=['echo v3.0'])

``none``
  This will return an empty string as the version. This is useful if you're
  using carthorse as a way of managing git tags or timestamped releases.

``env``
  This will extract the version from the specified environment variable. For example,
  if you have constructed the version in `$VERSION` you could extract it with:

  .. code-block:: toml

    [tool.carthorse]
    version-from = { name="env" }

  .. invisible-code-block: python

      run_config(expected_runs=['echo v4.0'])

  If you need to extract it from an environment variable with a different name, for example
  `$MYVERSION`, you could extract it with:

  .. code-block:: toml

    [tool.carthorse]
    version-from = { name="env", variable="MYVERSION" }

  .. invisible-code-block: python

      run_config(expected_runs=['echo v5.0'])

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

  If you are using carthorse to manage tags per environment, for example, you can ask for existing
  tags to be updated as follows:

  .. code-block:: toml

    [tool.carthorse]
    actions = [
       { name="create-tag", update=true},
    ]

  .. invisible-code-block: python

      run_config(expected_phrases=['git push --force origin tag v4.0'])
