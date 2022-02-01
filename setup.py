from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in nbpos/__init__.py
from nbpos import __version__ as version

setup(
	name="nbpos",
	version=version,
	description="nbpos",
	author="swapnil",
	author_email="swapnil.pawar",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
