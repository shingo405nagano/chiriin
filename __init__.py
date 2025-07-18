"""
Chiriin - 国土地理院のAPIやパラメーターファイルを利用するモジュール
"""

# よく使われるクラスと関数を直接インポート可能にする
from chiriin.config import MAG_DATA, XY, XYZ, ChiriinWebApi, Scope, TileData
from chiriin.features import calculate_mean_slope_in_polygon
from chiriin.formatter import type_checker_crs, type_checker_float, type_checker_shapely
from chiriin.geometries import degree_to_dms, dms_to_degree, get_projection
from chiriin.mag import MagDeclination
from chiriin.mesh import MeshCode
from chiriin.paper import MapEditor
from chiriin.semidynamic import SemiDynamic
from chiriin.tile import download_tile, get_tile_info
from chiriin.web import (
    fetch_distance_and_azimuth,
    fetch_elevation,
    fetch_geoid_height,
    fetch_semidynamic_2d,
    fetch_semidynamic_3d,
)

__version__ = "1.0.0"
__all__ = [
    # Config
    "MAG_DATA",
    "XY",
    "XYZ",
    "Scope",
    "TileData",
    "ChiriinWebApi",
    # Features
    "calculate_mean_slope_in_polygon",
    # Formatter
    "type_checker_float",
    "type_checker_crs",
    "type_checker_shapely",
    # Geometries
    "dms_to_degree",
    "degree_to_dms",
    "get_projection",
    # Mesh
    "MeshCode",
    # Mag
    "MagDeclination",
    # Semidynamic
    "SemiDynamic",
    # Paper
    "MapEditor",
    # Tile
    "get_tile_info",
    "download_tile",
    # Web
    "fetch_elevation",
    "fetch_geoid_height",
    "fetch_semidynamic_2d",
    "fetch_semidynamic_3d",
    "fetch_distance_and_azimuth",
]
