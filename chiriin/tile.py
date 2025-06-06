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
            タイルの左上の座標を表す辞書。
            'X'キーには緯度、'Y'キーには経度のリストが含まれます。
    """
    return {"X": [], "Y": []}


@type_checker_float(arg_index=0, kward="x")
@type_checker_float(arg_index=1, kward="y")
@type_checker_integer(arg_index=2, kward="zoom_level")
@type_checker_crs(arg_index=3, kward="in_crs")
def search_tile_info_from_xy(
    x: float,
    y: float,
    zoom_level: int,
    in_crs: str | int | pyproj.CRS,
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
    Returns:
        TileInfo:
            指定された座標とズームレベルに対応するタイルの情報を含むTileInfoオブジェクト。
            - x(int): タイルのx座標
            - y(int): タイルのy座標
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
    return TileInfo(
        x=0,
        y=0,
        zoom_level=zoom_level,
        tile_scope=TileScope(x_min=0, y_min=0, x_max=0, y_max=0),
        x_resolution=0.0,
        y_resolution=0.0,
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
