import numpy as np
import pyproj
import shapely

from chiriin.drawer import chiriin_drawer


def calc_slope(dtm: np.ndarray, x_resol: float, y_resol: float) -> np.ndarray:
    """
    ---------------------------------------------------------------------------
    ## Summary:
        標高データから傾斜を計算する関数
    ---------------------------------------------------------------------------
    Args:
        dtm (np.ndarray):
            標高データの2次元配列
        x_resol (float):
            x方向の解像度（メートル単位）
        y_resol (float):
            y方向の解像度（メートル単位）
    ---------------------------------------------------------------------------
    Returns:
        np.ndarray:
            傾斜の2次元配列（度単位）
    """
    dy, dx = np.gradient(dtm, y_resol, x_resol)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)
    return slope_deg.astype(np.float16)


def calculate_mean_slope_in_polygon(
    poly: shapely.Polygon,
    in_crs: str | int | pyproj.CRS,
) -> float:
    """
    ---------------------------------------------------------------------------
    ## Summary:
        指定したポリゴン内の平均傾斜を計算する関数
    ---------------------------------------------------------------------------
    Args:
        poly (shapely.Polygon):
            ポリゴンジオメトリ
        in_crs (str | int | pyproj.CRS):
            入力データの投影法。この投影法はメルカトル図法である必要があります。
    ---------------------------------------------------------------------------
    Returns:
        float:
            平均傾斜（度単位）
    """
    resps = chiriin_drawer.fetch_elevation_tile_mesh_with_dem10b(poly, 14, in_crs)
    means = []
    for tile_data in resps:
        x_range = np.arange(
            tile_data.tile_scope.x_min,
            tile_data.tile_scope.x_max,
            tile_data.x_resolution,
        )
        if 256 < x_range.size:
            x_range = x_range[:256]
        y_range = np.arange(
            tile_data.tile_scope.y_min,
            tile_data.tile_scope.y_max,
            tile_data.y_resolution,
        )
        if 256 < y_range.size:
            y_range = y_range[:256]
        slope = calc_slope(tile_data.ary, tile_data.x_resolution, tile_data.y_resolution)
        means.append(np.mean(slope))
    return float(np.mean(means))
