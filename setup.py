import os
from setuptools import find_packages, setup

# Load README file for long description.
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Main setup and configuration.
setup(
    name='flask-restfuloauth2',
    version='0.10.0',
    packages=find_packages(),
    include_package_data=True,
    license='Apache License Version 2.0',
    description='A Flask REST endpoint protected with OAuth2.',
    long_description=README,
    url='https://github.com/marcbperez/flask-restfuloauth2',
    author='marcbperez',
    author_email='marcbperez@users.noreply.github.com',
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-oauthlib',
        'bcrypt',
        'pyopenssl',
        'flask-restful',
        'flask-cors',
    ],
    setup_requires=[
        'pytest-runner',
        'setuptools-pep8',
    ],
    tests_require=[
        'pep8',
        'pytest-cov',
        'pytest',  # Keep at the end to avoid conflicts.
    ],
)
