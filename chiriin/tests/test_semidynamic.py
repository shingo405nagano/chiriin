import datetime
import os
from decimal import Decimal

import pandas as pd
import pytest

from chiriin.config import Delta, MeshDesign
from chiriin.semidynamic import SemiDynamic

test_prefecture_file = os.path.join(
    os.path.dirname(__file__), "data", "prefecture_pnt.csv"
)
df = pd.read_csv(test_prefecture_file)


@pytest.mark.parametrize(
    "lon, lat, altitude",
    [
        (139.6917, 35.6895, 0.0),
        (135.5023, 34.6937, 10.0),
        ([139.6917, 135.5023], [35.6895, 34.6937], [0.0, 10.0]),
    ],
)
def test_convert_lon_lat_from_semidynamic(lon, lat, altitude):
    """Test the conversion of longitude and latitude using semidynamic correction."""
    semidynamic = SemiDynamic(lon, lat, datetime.datetime(2024, 4, 1, 0, 0, 0), altitude)


def test_read_parameters_from_semidynamic():
    """Test reading parameters from semidynamic correction."""
    semidynamic = SemiDynamic(
        139.6917, 35.6895, datetime.datetime(2024, 4, 1, 0, 0, 0), 0.0
    )
    df = semidynamic._read_parameters()
    assert isinstance(df, pd.DataFrame), "Returned value should be a DataFrame"


def test_adjust_mesh_code_from_semidynamic():
    """Test adjusting mesh code from semidynamic correction."""
    semidynamic = SemiDynamic(
        lon=139.6917,
        lat=35.6895,
        altitude=0.0,
        datetime_=datetime.datetime(2022, 4, 1, 0, 0, 0),
    )
    mesh_design = semidynamic._adjust_mesh_code(
        lower_left_sec_lon=float(semidynamic.lon * 3600),
        lower_left_sec_lat=float(semidynamic.lat * 3600),
    )
    assert isinstance(mesh_design, MeshDesign), (
        "Returned value should be a MeshDesign instance"
    )
    assert isinstance(mesh_design.lon, float)
    assert 0 < mesh_design.lon
    assert isinstance(mesh_design.lat, float)
    assert 0 < mesh_design.lat
    assert isinstance(mesh_design.standard_mesh_code, str)
    assert len(mesh_design.standard_mesh_code) == 8


@pytest.mark.parametrize(
    (
        "lon, lat, lower_left_mesh_code, lower_right_mesh_code, "
        "upper_left_mesh_code, upper_right_mesh_code"
    ),
    [
        (140.463488, 40.608410, "60407305", "60407400", "60407355", "60407450"),
        (141.344604, 43.063119, "64414255", "64414350", "64415205", "64415300"),
    ],
)
def test_mesh_design_from_semidynamic(
    lon,
    lat,
    lower_left_mesh_code,
    lower_right_mesh_code,
    upper_left_mesh_code,
    upper_right_mesh_code,
):
    """Test mesh design from semidynamic correction."""
    semidynamic = SemiDynamic(lon, lat, datetime.datetime(2024, 4, 1, 0, 0, 0), 0.0)
    mesh_design = semidynamic.mesh_design(lon, lat)
    assert isinstance(mesh_design, dict), (
        "Returned value should be a dictionary containing MeshDesign instances"
    )
    assert mesh_design["lower_left"].standard_mesh_code == lower_left_mesh_code
    assert mesh_design["lower_right"].standard_mesh_code == lower_right_mesh_code
    assert mesh_design["upper_left"].standard_mesh_code == upper_left_mesh_code
    assert mesh_design["upper_right"].standard_mesh_code == upper_right_mesh_code


@pytest.mark.parametrize(
    "mesh_code, success",
    [
        ("64415300", True),
        (60407450, True),
        (60407305.0, True),
        ("99999999", False),  # Invalid mesh code
    ],
)
def test_get_delta_from_semidynamic(mesh_code, success):
    """Test getting delta values from semidynamic correction."""
    semidynamic = SemiDynamic(
        139.6917, 35.6895, datetime.datetime(2024, 4, 1, 0, 0, 0), 0.0
    )
    if success:
        delta = semidynamic._get_delta(mesh_code)
        assert isinstance(delta, Delta), "Returned value should be a Delta instance"
        assert isinstance(delta.delta_x, Decimal)
    else:
        with pytest.raises(Exception):  # noqa: B017
            semidynamic._get_delta(mesh_code)


def test_get_delta_sets_from_semidynamic():
    """Test that the delta values are correctly set from semidynamic correction."""
    semidynamic = SemiDynamic(
        139.6917, 35.6895, datetime.datetime(2024, 4, 1, 0, 0, 0), 0.0
    )
    mesh_design = semidynamic.mesh_design(float(semidynamic.lon), float(semidynamic.lat))
    delta_sets = semidynamic._get_delta_sets(mesh_design)
    assert isinstance(delta_sets, dict), "Returned value should be a dictionary"
    for delta in delta_sets.values():
        assert isinstance(delta, Delta), "Value should be a Delta instance"
        assert isinstance(delta.delta_x, Decimal)
        assert isinstance(delta.delta_y, Decimal)
        assert isinstance(delta.delta_z, Decimal)
