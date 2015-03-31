#!/usr/bin/env python
"""
sentry-gitlab
=============

An extension for Sentry which integrates with GitLab. Specifically, it allows
you to easily create issues from events within Sentry.

:copyright: (c) 2015 Pancentric Ltd, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'nose',
]

install_requires = [
    'sentry>=5.0.0',
    'python-gitlab>=0.4',
    'requests>=2.0',
]

setup(
    name='sentry-gitlab',
    version='0.2.0',
    author='Alex Crowe',
    author_email='alex@pancentric.com',
    url='http://github.com/ajcrowe/sentry-gitlab',
    description='A Sentry extension which integrates with GitLab.',
    long_description=__doc__,
    license='BSD',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'gitlab = sentry_gitlab',
        ],
        'sentry.plugins': [
            'gitlab = sentry_gitlab.plugin:GitLabPlugin'
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
