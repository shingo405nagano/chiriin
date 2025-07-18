"""
Chiriin - 国土地理院のAPIやパラメーターファイルを利用するモジュール
"""

# よく使われるクラスと関数を直接インポート可能にする
from .config import MAG_DATA, XY, XYZ, ChiriinWebApi, Scope, TileData
from .drawer import chiriin_drawer, map_editor
from .features import calculate_mean_slope_in_polygon
from .formatter import type_checker_crs, type_checker_float, type_checker_shapely
from .geometries import degree_to_dms, dms_to_degree
from .mag import get_magnetic_declination
from .mesh import MeshCode
from .paper import MapEditor
from .semidynamic import SemiDynamic

__version__ = "1.0.0"
__all__ = [
    # Drawer
    "chiriin_drawer",
    "map_editor",
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
    # Mesh
    "MeshCode",
    # Mag
    "get_magnetic_declination",
    # Semidynamic
    "SemiDynamic",
    # Paper
    "MapEditor",
]
