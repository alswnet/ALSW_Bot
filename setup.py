from setuptools import find_packages
from setuptools import setup

with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(
    name='alsw_bot',
    version='0.0.1',
    description='Bot Chat de ALSW',
    long_description=long_description,
    author='ChepeCarlos',
    author_email='chepecarlos@alswblog.org',
    url='https://github.com/chepecarlos/tooltube',
    install_requires=[],
    packages=find_packages(where='src', exclude=('tests*', 'testing*')),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'alswbot = alswbot.alswbot:main'
        ]
    },
)
