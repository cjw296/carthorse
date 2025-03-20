# See LICENSE.txt for license details.
# Copyright (c) 2019 onwards Chris Withers

from setuptools import setup, find_packages

setup(
    name='carthorse',
    version="2.0.3",
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description="Safely creating releases when you change the version number.",
    long_description=open('README.rst').read(),
    url="https://github.com/cjw296/carthorse",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    packages=find_packages(exclude=['tests']),
    python_requires=">=3.12",
    install_requires=[
        'pyyaml',
        'toml',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
            'sybil>=4',
            'testfixtures',
        ],
        'build': [
            'twine',
            'wheel'
        ]
    },
    entry_points={
        "console_scripts": [
            "carthorse = carthorse.cli:main",
        ],
        "carthorse.version_from": [
            "poetry = carthorse.version_from:poetry",
            "pyproject = carthorse.version_from:pyproject",
            "setup.py = carthorse.version_from:setup_py",
            "file = carthorse.version_from:file",
            "flit = carthorse.version_from:flit",
            "none = carthorse.version_from:none",
            "env = carthorse.version_from:env",
        ],
        "carthorse.when": [
            "version-not-tagged = carthorse.when:version_not_tagged",
            "never = carthorse.when:never",
            "always = carthorse.when:always",
        ],
        "carthorse.actions": [
            "run = carthorse.actions:run",
            "create-tag = carthorse.actions:create_tag",
            "update-major-tag = carthorse.actions:update_major_tag",
        ],
    },
)
