"""Setup file for drf-expiring-tokens."""
import os
import sys

from setuptools import setup, find_packages

import drf_expiring_tokens


version = drf_expiring_tokens.__version__

if sys.argv[-1] == 'publish':
    if os.system("pip list --format=legacy | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

setup(
    name='drf-expiring-tokens',
    version=version,
    description='Expiring Authentication Tokens for Django REST Framework',
    url=(
        'https://github.com/skrulcik/drf-expiring-tokens'
    ),
    author='Scott Krulcik',
    author_email='skrulcik@gmail.com',
    license='BSD',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'djangorestframework>=3.7,<3.8'
    ],
    test_suite='runtests.run',
    tests_require=[
        'Django>=1.11.8,<2.1'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
