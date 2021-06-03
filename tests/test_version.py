# -*- coding: utf-8 -*-


from bookops_worldcat.__version__ import (
    __version__,
    __title__,
    __author__,
    __author_email__,
)


def test_version():
    assert __version__ == "0.3.5"


def test_title():
    assert __title__ == "bookops-worldcat"


def test_author():
    assert __author__ == "Tomasz Kalata"


def test_author_email():
    assert __author_email__ == "klingaroo@gmail.com"
