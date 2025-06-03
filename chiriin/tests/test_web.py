import datetime
import os

import pandas as pd
import pytest

from chiriin.web import fetch_corrected_semidynamic_from_web, fetch_elevation_from_web

test_prefecture_file = os.path.join(
    os.path.dirname(__file__), "data", "prefecture_pnt.csv"
)
df = pd.read_csv(test_prefecture_file)
LON = df["longitude"].tolist()[:5]
LAT = df["latitude"].tolist()[:5]
ALTITUDE = df["altitude"].tolist()[:5]


def test_fetch_elevation_from_web():
    altitude_list = fetch_elevation_from_web(LON, LAT)
    assert isinstance(altitude_list, list)
    assert len(altitude_list) == len(LON)
    assert -100 < min(altitude_list) < 10000
    # Error
    altitude_list = fetch_elevation_from_web([340.00], [40.00])
    assert isinstance(altitude_list, list)
    assert not isinstance(altitude_list[0], float)


@pytest.mark.parametrize(
    "datetime_, dimension, return_to_original, err",
    [
        (datetime.datetime(2023, 10, 1, 0, 0, 0), 2, True, False),
        (datetime.datetime(2022, 10, 1, 0, 0, 0), 2, False, False),
        (datetime.datetime(2021, 10, 1, 0, 0, 0), 3, True, False),
        (datetime.datetime(2020, 10, 1, 0, 0, 0), 3, False, False),
        (datetime.datetime(2020, 10, 1, 0, 0, 0), 0, True, True),
    ],
)
def test_fetch_corrected_semidynamic_from_web(
    datetime_, dimension, return_to_original, err
):
    corrected_xyz = fetch_corrected_semidynamic_from_web(
        datetime_,
        LON if err is False else [340.00],
        LAT if err is False else [40.00],
        ALTITUDE if err is False else [0.0],
        dimension=dimension,
        return_to_original=return_to_original,
    )
    if err is False:
        assert isinstance(corrected_xyz, list)
        assert len(corrected_xyz) == len(LON)
        for coords in corrected_xyz:
            assert isinstance(coords.x, float)
            assert isinstance(coords.y, float)
            assert isinstance(coords.z, float)
            if dimension == 2:
                assert coords.z == 0.0
            else:
                assert coords.z != 0.0
    else:
        for coords in corrected_xyz:
            assert isinstance(coords, None)
