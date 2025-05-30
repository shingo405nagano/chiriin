"""
1. "10進法経緯度"から"度分秒経緯度"への変換
2. "度分秒経緯度"から"10進法経緯度"への変換
3. どちらの経緯度でも、求める単位に変換（リストも可）
"""

from decimal import Decimal
from typing import Iterable

from chiriin.config import XY
from chiriin.utils import dimensional_count


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
    """
    try:
        dms = float(dms)
    except ValueError as err:
        raise ValueError("dms must be a float or convertible to float.") from err
    dms_txt = str(dms)
    sep = "."
    integer_part, decimal_part = dms_txt.split(sep)
    micro_sec = float(f"0.{decimal_part}")
    if len(integer_part) < 6 or 7 < len(integer_part):
        raise ValueError(f"dms must have a 6- or 7-digit integer part. Arg: {dms}")
    sec = Decimal(f"{(int(integer_part[-2:]) + micro_sec) / 3600}")
    min_ = Decimal(f"{int(integer_part[-4:-2]) / 60}")
    deg = Decimal(f"{float(int(integer_part[:-4]))}")
    if decimal_obj:
        return round(deg + min_ + sec, digits)
    return float(round(deg + min_ + sec, digits))


def degree_to_dms(degree: float, digits: int = 5, decimal_obj: bool = False) -> float | Decimal:
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
    """
    try:
        _degree = float(degree)
    except ValueError as err:
        # 10進法経緯度はfloatに変換可能な値である必要がある
        raise ValueError("degree must be a float or convertible to float.") from err
    if not (-180 <= _degree <= 180):
        # 経度は-180から180の範囲である必要がある
        raise ValueError(f"degree must be in the range of -180 to 180. Arg: {degree}")

    deg = int(degree)
    min_ = int((degree - deg) * 60)
    _sec = str((degree - deg - min_ / 60) * 3600)
    idx = _sec.find(".")
    sec = int(_sec[:idx] if idx != -1 else _sec)
    # マイクロ秒は小数点以下5桁までを想定
    micro_sec = int(round(int(_sec[idx + 1 :][: digits + 1]), digits) * 0.1)
    # 度分秒が10未満の場合は0を付与
    deg = f"0{deg}" if deg < 10 else str(deg)
    min_ = f"0{min_}" if min_ < 10 else str(min_)
    sec = f"0{sec}" if sec < 10 else str(sec)
    dms = float(f"{deg}{min_}{sec}.{micro_sec}")
    if decimal_obj:
        return Decimal(f"{dms:.{digits}f}")
    return dms


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
    deg_lon = dms_to_degree(lon, digits, decimal_obj)
    deg_lat = dms_to_degree(lat, digits, decimal_obj)
    return XY(x=deg_lon, y=deg_lat)


def _dms_to_degree_lonlat_list(
    lon_list: Iterable[float],
    lat_list: Iterable[float],
    decimal_obj: bool = False,
    digits: int = 9,
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
    assert len(lon_list) == len(lat_list), "lon_list and lat_list must have the same length." # type: ignore
    assert dimensional_count(lon_list) == 1, "lon_list must be a 1-dimensional iterable."# type: ignore
    assert dimensional_count(lat_list) == 1, "lat_list must be a 1-dimensional iterable."# type: ignore
    result = []
    for lon, lat in zip(lon_list, lat_list, strict=False):
        xy = _dms_to_degree_lonlat(lon, lat, digits, decimal_obj)
        result.append(xy)
    return result


def dms_to_degree_lonlat(
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
    if isinstance(lon, Iterable):
        return _dms_to_degree_lonlat_list(lon, lat, decimal_obj, digits)  # type: ignore
    return _dms_to_degree_lonlat(lon, lat, digits, decimal_obj)  # type: ignore


def _degree_to_dms_lonlat(lon: float, lat: float, digits: int = 5, decimal_obj: bool = False) -> XY:
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
    dms_lon = degree_to_dms(lon, digits, decimal_obj)
    dms_lat = degree_to_dms(lat, digits, decimal_obj)
    return XY(x=dms_lon, y=dms_lat)


def _degree_to_dms_lonlat_list(
    lon_list: Iterable[float], lat_list: Iterable[float], digits: int = 5, decimal_obj: bool = False
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
    assert len(lon_list) == len(lat_list), "lon_list and lat_list must have the same length."  # type: ignore
    assert dimensional_count(lon_list) == 1, "lon_list must be a 1-dimensional iterable."  # type: ignore
    assert dimensional_count(lat_list) == 1, "lat_list must be a 1-dimensional iterable."  # type: ignore
    result = []
    for lon, lat in zip(lon_list, lat_list, strict=False):
        xy = _degree_to_dms_lonlat(lon, lat, digits, decimal_obj)
        result.append(xy)
    return result


def degree_to_dms_lonlat(
    lon: float | Iterable[float],
    lat: float | Iterable[float],
    digits: int = 5,
    decimal_obj: bool = False,
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
    if isinstance(lon, Iterable):
        return _degree_to_dms_lonlat_list(lon, lat, digits, decimal_obj)  # type: ignore
    return _degree_to_dms_lonlat(lon, lat, digits, decimal_obj)  # type: ignore
