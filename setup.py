from setuptools import setup, find_packages

setup(
    name="pigeonpictures",
    version="1.1.4",
    author="Amir Eldor",
    author_email="amir@eize.ninja",
    packages=find_packages(),
    install_requires=["jinja2", "boto3"],
    tests_require=["pytest"],
)
