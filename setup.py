from setuptools import setup, find_packages

setup(
    name='project0',
    version='1.0',
    author='Vijay Kumar Reddy Gade',
    author_email='vi.gade@ufl.edu',
    packages=find_packages(exclude=('tests', 'docs', 'resources')),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=[
        'pypdf',  # we have to install pypdf, if not avlbl
    ],
)
