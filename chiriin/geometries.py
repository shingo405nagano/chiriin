"""
1. "10進法経緯度"から"度分秒経緯度"への変換
2. "度分秒経緯度"から"10進法経緯度"への変換
3. どちらの経緯度でも、求める単位に変換（リストも可）
"""

from decimal import Decimal
from typing import Iterable

from chiriin.config import XY


def dms_to_degree(dms: float, digits: int = 9, decimal_obj: bool = False) -> float | Decimal:
    """
    ## Description:
        度分秒経緯度を10進法経緯度に変換する関数
    ## Args:
        dms (float):
            度分秒経緯度
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            10進法経緯度をDecimal型で返すかどうか
    ## Returns:
        float | Decimal:
            10進法経緯度
    Example:
        >>> dms_to_degree(140516.27814)
        140.087855042
        >>> dms_to_degree(36103600.00000)
        36.103774792
    """
    pass


def degree_to_dms(degree: float, decimal_obj: bool = False, digits: int = 5) -> float | Decimal:
    """
    ## Description:
        10進法経緯度を度分秒経緯度に変換する関数
    ## Args:
        degree (float):
            10進法経緯度
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            度分秒経緯度をDecimal型で返すかどうか
    ## Returns:
        float | Decimal:
            度分秒経緯度
    Example:
        >>> degree_to_dms(140.08785504166664)
        140516.2781
        >>> degree_to_dms(36.103774791666666)
        36103600.0000
    """
    pass


def _dms_to_degree_lonlat(lon: float, lat: float, digits: int = 9, decimal_obj: bool = False) -> XY:
    """
    ## Description:
        度分秒経緯度を10進法経緯度に変換する関数
    ## Args:
        lon (float):
            度分秒経緯度
        lat (float):
            度分秒経緯度
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            Decimal型で返すかどうか
    ## Returns:
        XY(NamedTuple):
            10進法経緯度
            - x: float | Decimal
            - y: float | Decimal
    Example:
        >>> dms_to_degree_lonlat(140516.27814, 36103600.00000)
        (140.087855042, 36.103774792)
    """
    pass


def _dms_to_degree_lonlat_list(
    lon_list: Iterable[float], lat_list: Iterable[float], digits: int = 9, decimal_obj: bool = False
) -> list[XY]:
    """
    ## Description:
        リスト化された度分秒経緯度を10進法経緯度に変換する関数
    ## Args:
        lon_list (Iterable[float]):
            度分秒経緯度のリスト（経度）
        lat_list (Iterable[float]):
            度分秒経緯度のリスト（緯度）
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            Decimal型で返すかどうか
    ## Returns:
        list[XY(NamedTuple)]:
            10進法経緯度のリスト
            - x: float | Decimal
            - y: float | Decimal
    Example:
        >>> dms_to_degree_lonlat_list([140516.27814, 140516.27814], [36103600.00000, 36103600.00000])
        [(140.087855042, 36.103774792), (140.087855042, 36.103774792)]
    """
    pass


def dms_to_lonlat(
    lon: float | Iterable[float],
    lat: float | Iterable[float],
    digits: int = 9,
    decimal_obj: bool = False,
) -> XY | list[XY]:
    """
    ## Description:
        度分秒経緯度を10進法経緯度に変換する関数
    ## Args:
        lon (float | Iterable[float]):
            度分秒経緯度（経度）
        lat (float | Iterable[float]):
            度分秒経緯度（緯度）
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            Decimal型で返すかどうか
    ## Returns:
        XY | list[XY]:
            10進法経緯度
            - x: float | Decimal
            - y: float | Decimal
    """
    pass


def _degree_to_dms_lonlat(lon: float, lat: float, decimal_obj: bool = False, digits: int = 5) -> XY:
    """
    ## Description:
        10進法経緯度を度分秒経緯度に変換する関数
    ## Args:
        lon (float):
            10進法経緯度（経度）
        lat (float):
            10進法経緯度（緯度）
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            Decimal型で返すかどうか
    ## Returns:
        XY(NamedTuple):
            度分秒経緯度
            - x: float | Decimal
            - y: float | Decimal
    Example:
        >>> degree_to_dms_lonlat(140.08785504166664, 36.103774791666666)
        (140516.2781, 36103600.0000)
    """
    pass


def _degree_to_dms_lonlat_list(
    lon_list: Iterable[float], lat_list: Iterable[float], decimal_obj: bool = False, digits: int = 5
) -> list[XY]:
    """
    ## Description:
        リスト化された10進法経緯度を度分秒経緯度に変換する関数
    ## Args:
        lon_list (Iterable[float]):
            10進法経緯度のリスト（経度）
        lat_list (Iterable[float]):
            10進法経緯度のリスト（緯度）
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            Decimal型で返すかどうか
    ## Returns:
        list[XY(NamedTuple)]:
            度分秒経緯度のリスト
            - x: float | Decimal
            - y: float | Decimal
    Example:
        >>> degree_to_dms_lonlat_list([140.08785504166664, 140.08785504166664], [36.103774791666666, 36.103774791666666])
        [(140516.2781, 36103600.0000), (140516.2781, 36103600.0000)]
    """
    pass


def degree_to_lonlat(
    lon: float | Iterable[float], lat: float | Iterable[float], decimal_obj: bool = False, digits: int = 5
) -> XY | list[XY]:
    """
    ## Description:
        10進法経緯度を度分秒経緯度に変換する関数
    ## Args:
        lon (float | Iterable[float]):
            10進法経緯度（経度）
        lat (float | Iterable[float]):
            10進法経緯度（緯度）
        digits (int):
            小数点以下の桁数
        decimal_obj (bool):
            Decimal型で返すかどうか
    ## Returns:
        XY | list[XY]:
            度分秒経緯度
            - x: float | Decimal
            - y: float | Decimal
    """
    pass
