"""Test scalar coercion."""

import pytest
from datetime import datetime
from ramlpy.validator.scalars import coerce_scalar


def test_coerce_string():
    assert coerce_scalar("string", 123) == "123"


def test_coerce_integer():
    assert coerce_scalar("integer", "123") == 123


def test_coerce_integer_negative():
    assert coerce_scalar("integer", "-42") == -42


def test_coerce_integer_invalid():
    with pytest.raises(ValueError):
        coerce_scalar("integer", "abc")


def test_coerce_number():
    assert coerce_scalar("number", "3.14") == 3.14


def test_coerce_number_integer():
    assert coerce_scalar("number", "42") == 42.0


def test_coerce_number_invalid():
    with pytest.raises(ValueError):
        coerce_scalar("number", "abc")


def test_coerce_boolean_true():
    assert coerce_scalar("boolean", "true") is True
    assert coerce_scalar("boolean", "True") is True
    assert coerce_scalar("boolean", "1") is True
    assert coerce_scalar("boolean", "yes") is True


def test_coerce_boolean_false():
    assert coerce_scalar("boolean", "false") is False
    assert coerce_scalar("boolean", "False") is False
    assert coerce_scalar("boolean", "0") is False
    assert coerce_scalar("boolean", "no") is False


def test_coerce_boolean_native():
    assert coerce_scalar("boolean", True) is True
    assert coerce_scalar("boolean", False) is False


def test_coerce_boolean_invalid():
    with pytest.raises(ValueError):
        coerce_scalar("boolean", "maybe")


def test_coerce_none():
    assert coerce_scalar("string", None) is None
    assert coerce_scalar("integer", None) is None
