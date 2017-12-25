from io import open

from setuptools import find_packages, setup

with open('pytest_tipsi_testing/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.1.0'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = [
    'pytest>=3.3.0',
    # 'tipsi-tools>=1.7.0',
]

setup(
    name='pytest-tipsi-testing',
    version=version,
    description='Better fixtures management. Various helpers',
    long_description=readme,
    author='cybergrind',
    author_email='cybergrind@gmail.com',
    maintainer='cybergrind',
    maintainer_email='cybergrind@gmail.com',
    url='https://github.com/tipsi/pytest-tipsi-testing',
    license='MIT',

    keywords=[
        'pytest', 'helpers', 'fixtures', 'scopes', 'ordering',
    ],

    entry_points={
        'pytest11': ['pytest_tipsi_testing = pytest_tipsi_testing.plugin'],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    install_requires=REQUIRES,
    extras_require={
        'log_requests': ['requests==2.18.*'],
    },
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
