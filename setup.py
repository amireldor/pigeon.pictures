from setuptools import setup, find_packages

setup(
    name="pigeonpictures",
    version="1.1.0",
    author="Amir Eldor",
    author_email="amir@eize.ninja",
    packages=find_packages(),
    install_requires=["zappa", "jinja2", "boto3"],
)
