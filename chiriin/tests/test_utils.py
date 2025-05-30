import datetime

import numpy as np
import pytest

from chiriin.utils import datetime_formatter, dimensional_count


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
    "iterable, expected",
    [
        ("100", 0),
        (100, 0),
        (100.0, 0),
        ((100, 200), 1),
        ([100, 200], 1),
        ([[100, 200], [300, 400]], 2),
        ([[[100, 200], [300, 400]], [[500, 600], [700, 800]]], 3),
        (np.array([1, 2, 3]), 1),
        (np.array([[1, 2], [3, 4]]), 2),
    ],
)
def test_dimensional_count(iterable, expected):
    """Test dimensional_count function."""
    result = dimensional_count(iterable)
    assert result == expected
