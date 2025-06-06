import time
from typing import Optional

import numpy as np
import pyproj
import requests
import shapely

from chiriin.config import TileInfo, TileScope
from chiriin.formatter import (
    type_checker_crs,
    type_checker_float,
    type_checker_integer,
    type_checker_shapely,
    type_checker_zoom_level,
)


def download_tile_array(url: str) -> np.ndarray:
    """
    ## Summary:
        地理院の標高APIを利用して、指定されたURLからタイルデータを取得する関数です。
        タイルデータは`bytes`型で返されるので、Float型の`np.ndarray`に変換して返しマス。
    """
    max_retries = 5
    retries = 0
    while True:
        if max_retries < retries:
            raise Exception(
                "Max retries exceeded, unable to download tile data. "
                f"\nRequest URL: {url}"
            )
        try:
            response = requests.get(url)
            if response.status_code != 200:
                retries += 1
                time.sleep(0.5)
                continue
            response_content = response.content
            # np.ndarrayに変換する処理を追加
            # ここでは、タイルデータがテキスト形式であることを前提としています。
            # もしバイナリ形式であれば、適切な変換方法を使用してください。
            tile_txt = response_content.decode("utf-8")
            # 'e'を'-9999'に置き換え、NaNに変換するための処理
            tile_data = tile_txt.replace("e", "-9999").splitlines()
            tile_data = [[float(v) for v in line.split(",")] for line in tile_data]
        except Exception as e:
            print(f"Error downloading tile: {e}")
            time.sleep(1)
        else:
            break
    ary = np.array(tile_data, dtype=np.float32)
    ary[ary == -9999] = np.nan  # -9999をNaNに変換
    return ary


@type_checker_integer(arg_index=0, kward="zoom_level")
@type_checker_zoom_level(arg_index=0, kward="zoom_level", min_zl=0, max_zl=24)
def cut_off_points(zoom_level: int) -> dict[str, list[float]]:
    """
    ## Summary:
        'zoom_level'で指定した地図タイルの座標を計算する。
        地図タイルは左上から計算されるので、取得出来る座標も左上のものです。
    Args:
        zoom_level (int):
            ズームレベルを指定する整数値。
            0-24の範囲にある整数で指定する必要があります。
    Returns:
        dict[str, list[float]]:
            タイルの左上の座標を表す辞書。座標は`Web Mercator`座標系（EPSG:3857）です。
            'X'キーには緯度、'Y'キーには経度のリストが含まれます。
    """
    web_mercator_scope = TileScope()
    x_length = web_mercator_scope.x_max - web_mercator_scope.x_min
    y_length = web_mercator_scope.y_max - web_mercator_scope.y_min
    side = 2**zoom_level
    X = [web_mercator_scope.x_min + i * (x_length / side) for i in range(side + 1)]
    Y = [web_mercator_scope.y_min + i * (y_length / side) for i in range(side + 1)]
    Y.sort(reverse=True)
    return {"X": X, "Y": Y}


def _search_tile_index(search_value: float, values: list[float]) -> int:
    """
    ## Summary:
        指定された値が、与えられた値のリストのどの区間に属するかを検索する。
        区間は左閉右開で定義されている。
    Args:
        search_value (float):
            検索する値。
        values (list[float]):
            検索対象の値のリスト。値は昇順にソートされている必要があります。
    """
    for i, (left, right) in enumerate(zip(values[:-1], values[1:], strict=True)):
        min_ = min(left, right)
        max_ = max(left, right)
        if min_ <= search_value < max_:
            return i
    raise ValueError(
        f"Value {search_value} is out of bounds for the provided values:"
        f"min={min(values)}, max={max(values)}"
    )


@type_checker_float(arg_index=0, kward="x")
@type_checker_float(arg_index=1, kward="y")
@type_checker_crs(arg_index=3, kward="in_crs")
def search_tile_info_from_xy(
    x: float, y: float, zoom_level: int, in_crs: str | int | pyproj.CRS, **kwargs
) -> TileInfo:
    """
    ## Summary:
        指定した座標とズームレベルを含むタイルの情報を取得する。
        座標は"Iterable"な値を受け取らないので注意。
    Args:
        x(float):
            x座標
        y(float):
            y座標
        zoom_level(int):
            ズームレベルを指定する整数値。
            0-24の範囲にある整数で指定する必要があります。
        in_crs(str | int | pyproj.CRS):
            入力座標系を指定するオプションの引数。
            指定しない場合は、経緯度（EPSG:4326）として解釈されます。
        **kwargs:
            - width(int): タイルの幅（ピクセル単位）。デフォルトは256。
            - height(int): タイルの高さ（ピクセル単位）。デフォルトは256。
    Returns:
        TileInfo:
            指定された座標とズームレベルに対応するタイルの情報を含むTileInfoオブジェクト。
            - x_idx(int): タイルのx座標
            - y_idx(int): タイルのy座標
            - zoom_level(int): ズームレベル
            - tile_scope(TileScope): タイルの範囲を表す(x_min, y_min, x_max, y_max)
                                    を含むTileScopeオブジェクト
            - x_resolution(float): タイルのx方向の解像度
            - y_resolution(float): タイルのy方向の解像度
            - width(int): タイルの幅（ピクセル単位）。デフォルトは256。
            - height(int): タイルの高さ（ピクセル単位）。デフォルトは256。
            - in_crs(pyproj.CRS): 入力座標系を表すpyproj.CRSオブジェクト。
                                  デフォルトはEPSG:3857（Web Mercator）です。
    """
    if in_crs.to_epsg() != 3857:
        # 入力座標系がWeb Mercatorでない場合、変換を行う
        transformer = pyproj.Transformer.from_crs(in_crs, "EPSG:3857", always_xy=True)
        x, y = transformer.transform(x, y)
    tile_cds = cut_off_points(zoom_level)
    x_idx = _search_tile_index(x, tile_cds["X"])
    y_idx = _search_tile_index(y, tile_cds["Y"])
    tile_scope = TileScope(
        x_min=tile_cds["X"][x_idx],
        y_min=tile_cds["Y"][y_idx + 1],
        x_max=tile_cds["X"][x_idx + 1],
        y_max=tile_cds["Y"][y_idx],
    )
    width = kwargs.get("width", 256)
    height = kwargs.get("height", 256)
    x_resolution = (tile_scope.x_max - tile_scope.x_min) / width
    y_resolution = (tile_scope.y_max - tile_scope.y_min) / height
    return TileInfo(
        x_idx=x_idx,
        y_idx=y_idx,
        zoom_level=zoom_level,
        tile_scope=tile_scope,
        x_resolution=round(x_resolution, 4),
        y_resolution=round(y_resolution, 4),
    )


@type_checker_shapely(arg_index=0, kward="geometry")
@type_checker_integer(arg_index=1, kward="zoom_level")
@type_checker_crs(arg_index=2, kward="in_crs")
def search_tile_info_from_geometry(
    geometry: shapely.geometry.base.BaseGeometry,
    zoom_level: int,
    in_crs: Optional[str | pyproj.CRS] = None,
) -> TileInfo | list[TileInfo]:
    """
    ## Summary:
        指定したジオメトリとズームレベルを含むタイルの情報を取得する。
        ジオメトリはshapelyのBaseGeometryオブジェクトで指定します。
        ジオメトリの範囲が複数のタイルにまたがる場合は、listで返されます。
    Args:
        geometry(shapely.geometry.base.BaseGeometry):
            タイルを検索するためのジオメトリ。
        zoom_level(int):
            ズームレベルを指定する整数値。
            0-24の範囲にある整数で指定する必要があります。
        in_crs(Optional[str | pyproj.CRS]):
            入力座標系を指定するオプションの引数。
            指定しない場合は、経緯度（EPSG:4326）として解釈されます。
    Returns:
        TileInfo | list[TileInfo]:
            指定されたジオメトリとズームレベルに対応するタイルの情報を含むTileInfoオブジェクト。
    """
    return TileInfo(
        x=0,
        y=0,
        zoom_level=zoom_level,
        tile_scope=TileScope(x_min=0, y_min=0, x_max=0, y_max=0),
        x_resolution=0.0,
        y_resolution=0.0,
    )
