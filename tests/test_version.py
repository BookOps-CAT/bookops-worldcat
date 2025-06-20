# -*- coding: utf-8 -*-


from bookops_worldcat.__version__ import (
    __author__,
    __author_email__,
    __title__,
    __version__,
)


def test_version():
    assert __version__ == "1.2.0"


def test_title():
    assert __title__ == "bookops-worldcat"


def test_author():
    assert __author__ == "Tomasz Kalata"


def test_author_email():
    assert __author_email__ == "klingaroo@gmail.com"
