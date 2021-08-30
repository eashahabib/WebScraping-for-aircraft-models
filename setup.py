from os import name
from setuptools import setup
from setuptools import find_packages

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name = 'aircraft_model_scraper',
    version = '0.0.6',
    description = 'This package scrapes difference websites online to create a comprehensive aircraft dataset',
    long_description=README,
    long_description_content_type="text/markdown",
    url = 'https://github.com/eashahabib/Webscraper-for-aircraft-models',
    author = 'Easha Habib',
    license = 'MIT',
    packages = find_packages(),
    install_requires = ['requests', 'beautifulsoup4', 'pandas', 'sqlalchemy', 'tqdm', 'selenium', 'openpyxl'],
)