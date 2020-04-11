from setuptools import setup, find_packages

setup(
    name="pigeonpictures",
    version="1.2.4",
    author="Amir Eldor",
    author_email="amir@eldor.dev",
    packages=find_packages(),
    install_requires=["jinja2", "boto3"],
    tests_require=["pytest"],
)
