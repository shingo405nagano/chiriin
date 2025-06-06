import pytest

from chiriin.config import ElevationTileUrl
from chiriin.tile import download_tile_array

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
