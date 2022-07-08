from setuptools import setup

import huey_django_orm

author = "avryhof"
name = huey_django_orm.name
version = huey_django_orm.__version__

readme = open("README.md").read()

setup(
    name=name,
    version=version,
    packages=[name],
    include_package_data=True,
    url="https://github.com/{}/{}".format(author, name),
    project_urls={
        "GitHub Repo": "https://github.com/{}/{}".format(author, name),
        "Bug Tracker": "https://github.com/{}/{}/issues".format(author, name),
    },
    license="MIT",
    author="Amos Vryhof",
    author_email="avryhof@gmail.com",
    description="A module to use Django ORM for storage with huey.",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="huey,django,huey.contrib.djhuey",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["Django", "huey"],
)
