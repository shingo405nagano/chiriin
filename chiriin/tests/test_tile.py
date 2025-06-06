import pytest
import shapely

from chiriin.config import ElevationTileUrl, TileInfo, TileScope
from chiriin.tile import (
    cut_off_points,
    download_tile_array,
    search_tile_info_from_geometry,
    search_tile_info_from_xy,
)

elev_tile_url = ElevationTileUrl()


@pytest.mark.parametrize(
    "url, success",
    [
        (elev_tile_url.dem_10b(14, 14624, 6017), True),
        (elev_tile_url.dem_10b(10, 14624, 6017), False),
    ],
)
def test_download_tile_array(url, success):
    if success:
        ary = download_tile_array(url)
        assert ary.shape == (256, 256)
        assert ary.dtype == "float32"
    else:
        with pytest.raises(Exception):  # noqa: B017
            download_tile_array(url)


def test_cut_off_points():
    """Test the cut_off_points function."""
    preview = 0
    for zl in range(0, 25):
        points = cut_off_points(zl)
        assert isinstance(points, dict)
        assert "Y" in points
        assert "X" in points
        assert preview < len(points["X"])
        assert preview < len(points["Y"])
        preview = len(points["X"]) * len(points["Y"])

    with pytest.raises(ValueError):
        cut_off_points(-1)

    with pytest.raises(ValueError):
        cut_off_points("invalid")  # type: ignore


def test_tile_info_from_xy():
    """Test the search_tile_info_from_xy function."""
    lon = 140.3158733
    lat = 38.3105495
    crs = "EPSG:4326"
    preview_x_resol = 0
    preview_y_resol = 0
    preview_width = 0
    preview_height = 0
    for zl in sorted(list(range(0, 25)), reverse=True):
        tile_info = search_tile_info_from_xy(lon, lat, zl, in_crs=crs)
        assert isinstance(tile_info, TileInfo)
        assert preview_x_resol < tile_info.x_resolution
        assert preview_y_resol < tile_info.y_resolution
        assert preview_width < tile_info.width
        assert preview_height < tile_info.height


def test_tile_info_from_geometry():
    """Test the search_tile_info_from_geometry function."""
    geom = shapely.Point(140.3158733, 38.3105495).buffer(0.5).envelope
    crs = "EPSG:4326"
    tile_geoms = []
    for zl in sorted(list(range(0, 25)), reverse=True):
        tile_info = search_tile_info_from_geometry(geom, zl, in_crs=crs)
        if isinstance(tile_info, list):
            assert all(isinstance(ti, TileInfo) for ti in tile_info)
        else:
            assert isinstance(tile_info, TileInfo)
            tile_info = [tile_info]
        for tl in tile_info:
            scope = shapely.box(*tl.tile_scope)
            tile_geoms.append(scope)

    result_tile_scope = TileScope(*shapely.union_all(tile_geoms).bounds)
    geom_scope = TileScope(*geom.bounds)
    assert result_tile_scope.x_min <= geom_scope.x_min
    assert result_tile_scope.y_min <= geom_scope.y_min
    assert geom_scope.x_max <= result_tile_scope.x_max
    assert geom_scope.y_max <= result_tile_scope.y_max
