import datetime

import pytest

from chiriin.formatter import (
    datetime_formatter,
    type_checker_datetime,
    type_checker_float,
    type_checker_integer,
)


@pytest.mark.parametrize(
    "datetime_",
    [
        "2023-11-16T11:06:21.700+09:00",
        "2023-11-16T11:06:21.700",
        "2023-11-16 11:06:21",
        "2023-11-16",
        "2023/11/16 11:06:21",
        "2023/11/16 11:06",
        datetime.datetime(2023, 11, 16, 11, 6, 21, 700000),
    ],
)
def test_datetime_formatter(datetime_):
    """Test datetime_formatter function."""
    result = datetime_formatter(datetime_)
    assert isinstance(result, datetime.datetime)
    with pytest.raises(ValueError):
        datetime_formatter("invalid datetime string")
    with pytest.raises(TypeError):
        datetime_formatter(12345)  # type: ignore


@pytest.mark.parametrize(
    "value, expected, success",
    [
        (1, 1.0, True),
        (1.0, 1.0, True),
        (1.5, 1.5, True),
        ("1", 1.0, True),
        ("10-", None, False),
    ],
)
def test_type_checker_float(value, expected, success):
    @type_checker_float(arg_index=0, kward="value")
    def dummy_function(value: float):
        return value

    if success:
        result = dummy_function(value)
        # result = dummy_function(value=value)
        assert isinstance(result, float)
        assert result == expected
    else:
        with pytest.raises(TypeError):
            dummy_function(value)


@pytest.mark.parametrize(
    "value, expected, success",
    [
        (1, 1, True),
        (1.0, 1, True),
        ("1", 1, True),
        ("10-", None, False),
    ],
)
def test_type_checker_integer(value, expected, success):
    @type_checker_integer(arg_index=0, kward="value")
    def dummy_function(value: int):
        return value

    if success:
        result = dummy_function(value)
        # result = dummy_function(value=value)
        assert isinstance(result, int)
        assert result == expected
    else:
        with pytest.raises(TypeError):
            dummy_function(value)


@pytest.mark.parametrize(
    "datetime_, success",
    [
        ("2023-11-16T11:06:21.700+09:00", True),
        ("2023-11-16T11:06:21.700", True),
        ("2023-11-16 11:06:21", True),
        ("2023-11-16", True),
        ("2023/11/16 11:06:21", True),
        ("2023/11/16 11:06", True),
        (datetime.datetime(2023, 11, 16, 11, 6, 21, 700000), True),
        ("invalid datetime string", False),
        (12345, False),  # type: ignore
    ],
)
def test_type_checker_datetime(datetime_, success):
    @type_checker_datetime(arg_index=0, kward="datetime_")
    def dummy_function(datetime_: datetime.datetime):
        return datetime_

    if success:
        result = dummy_function(datetime_)
        result = dummy_function(datetime_=datetime_)
        assert isinstance(result, datetime.datetime)
        assert result.microsecond == 0
    else:
        with pytest.raises((ValueError, TypeError)):
            dummy_function(datetime_)
