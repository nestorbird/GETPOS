from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in nbpos/__init__.py
from getpos import __version__ as version

setup(
	name="getpos",
	version=version,
	description="getpos",
	author="Nestorbird",
	author_email="info@nestorbird.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
