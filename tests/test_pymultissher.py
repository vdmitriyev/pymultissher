#!/usr/bin/env python

"""Tests for `pymultissher` package."""

import pytest

import pymultissher as pymultissher


@pytest.fixture
def response_fix():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    pass


def test_license(response_fix):
    assert pymultissher.__license__ == "MIT"
