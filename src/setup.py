# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="wsserver",
    version="0.2",
    description="Small websocket server",
    long_description="",
    author="Arseny Turin",
    author_email="arseniy.ny@gmail.com",
    url="https://github.com/arseniyturin/python-websocket",
    license="MIT",
    package=find_packages(exclude=("tests", "docs")),
)