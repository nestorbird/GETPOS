from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in agribora/__init__.py
from agribora import __version__ as version

setup(
	name="agribora",
	version=version,
	description="data driven agribusiness",
	author="www.nestorbird.com",
	author_email="info@nestorbird.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
