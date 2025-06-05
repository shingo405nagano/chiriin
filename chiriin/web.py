import asyncio
import datetime
import time
from pprint import pprint
from typing import Union

import aiohttp
from pydantic import ValidationError

from chiriin.config import XYZ, ChiriinWebApi

chiriin_web_api = ChiriinWebApi()


# ***********************************************************************
# **************** 地理院APIで標高値を取得する非同期処理 ****************
# ***********************************************************************
async def fetch_elevation(
    session: aiohttp.client.ClientSession,
    index: int,
    lon: float,
    lat: float,
    max_retry: int = 5,
    time_out: int = 10,
) -> dict[int, float]:
    """
    ## Description:
        地理院APIで標高値を取得する
    Args:
        session(aiohttp.client.ClientSession): セッション
        index(int): インデックス
        lon(float): 経度
        lat(float): 緯度
        max_retry(int): リトライ回数
        time_out(int): タイムアウト
    Returns:
        dict[int, float]: {index: elevation}
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    }
    url = chiriin_web_api.elevation_url().format(lon=lon, lat=lat)
    for _ in range(max_retry):
        try:
            async with session.get(url, headers=headers, timeout=time_out) as response:
                data = await response.json()
                if data.get("ErrMsg") is None:
                    print(
                        f"Idx: {index}  標高: {data['elevation']}m (lon: {lon}, lat: {lat})"
                    )
                    return {index: data["elevation"]}
                else:
                    print("サーバーが混みあっています。")
        except aiohttp.ClientError:
            print(
                f"リクエストに失敗しました (Index: {index}, lon: {lon}, lat: {lat})。再試行中..."
            )
    return {index: None}


async def fetch_elevation_main(
    idxs: list[int], lons: list[float], lats: list[float], time_sleep: int = 10
) -> list[dict[int, float]]:
    """
    ## Description:
        地理院APIで標高値を取得するメイン処理
    Args:
        idxs(list[int]): インデックス
        lons(list[float]): 経度
        lats(list[float]): 緯度
        time_sleep(int): 待ち時間。地理院APIのリクエスト制限による
    Returns:
        list[dict[int, float]]: [{index: elevation}]
    """
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, lon, lat in zip(idxs, lons, lats, strict=False):
            task = fetch_elevation(session, idx, lon, lat)
            tasks.append(task)
            if len(tasks) == 10:
                results += await asyncio.gather(*tasks)
                tasks = []
                time.sleep(time_sleep)
        if tasks:
            results += await asyncio.gather(*tasks)
    return results


def fetch_elevation_from_web(lons: list[float], lats: list[float]) -> list[float]:
    """
    ## Description:
        非同期処理により、地理院APIで標高値を取得する
    Args:
        lons(list[float]): 10進経度
        lats(list[float]): 10進緯度
    Returns:
        list[float]: 標高値
    Examples:
        >>> lons = [141.272242456]
        >>> lats = [40.924881316]
        >>> fetch_elevation_from_web(lons, lats)
        Idx: 0  標高: 84m (lon: 141.272242456, lat: 40.924881316)
        [84]
    """
    idxs = list(range(len(lons)))
    resps_lst = asyncio.run(fetch_elevation_main(idxs, lons, lats))
    _data = {}
    for resp in resps_lst:
        _data.update(resp)
    sorted_keys = sorted(_data.keys())
    sorted_elev = [_data[key] for key in sorted_keys]
    return sorted_elev


# ***********************************************************************
# **************** 地理院APIでセミダイナミック補正を行う ****************
# ***********************************************************************


async def fetch_corrected_semidynamic(
    session: aiohttp.client.ClientSession,
    index: int,
    correction_datetime: datetime.datetime,
    lon: float,
    lat: float,
    alti: float = 0.0,
    max_retry: int = 5,
    time_out: int = 10,
    dimension: int = 2,
    return_to_original: bool = True,
) -> dict[int, float]:
    """
    ## Description:
        地理院APIでセミダイナミック補正を行う
    Args:
        session(aiohttp.client.ClientSession): セッション
        index(int): インデックス
        correction_datetime(Union[str, int, datetime.datetime]): 補正日時
        lon(float): 経度
        lat(float): 緯度
        alti(float): 標高。標高は指定しなくとも問題はない。
        max_retry(int): リトライ回数
        time_out(int): タイムアウト
        dimension(int): 2次元補正を行う場合は2、3次元補正を行う場合は3
        return_to_original(bool): Trueなら今期から元期に変換、Falseならば元期から今期へ変換
    Returns:
        dict[int, float]: {index: Coords}
            - Coords: NamedTuple(longitude: float, latitude: float, altitude: float))
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    }
    try:
        url = chiriin_web_api.semidynamic_correction_url().format(
            year=correction_datetime.year,
            sokuchi=1 if return_to_original else 0,
            dimension=dimension,
            lon=lon,
            lat=lat,
            alti=alti,
        )
    except ValidationError as e:
        pprint(e.errors())
    for _ in range(max_retry):
        try:
            async with session.get(url, headers=headers, timeout=time_out) as response:
                data = await response.json()
                if data.get("ErrMsg") is None:
                    data = data.get("OutputData")
                    if data.get("altitude") == {}:
                        z = 0.0
                    else:
                        z = float(data["altitude"])
                    x = float(data["longitude"])
                    y = float(data["latitude"])
                    data = XYZ(x=x, y=y, z=z)
                    print(
                        f"Request   => Lon: {lon}, Lat: {lat}, Alt: {alti}m\n"
                        f"Corrected => Lon: {data.x}, Lat: {data.y}, Alt: {data.z}m\n"
                    )
                    return {index: data}
                else:
                    print(f"サーバーが混みあっています。ErrMsg: {data.get('ErrMsg')}")
        except aiohttp.ClientError:
            print(
                f"リクエストに失敗しました (Index: {index}, lon: {lon}, lat: {lat})。再試行中..."
            )
    return {index: None}


async def fetch_corrected_semidynamic_main(
    idxs: list[int],
    correction_datetime: Union[str, int, datetime.datetime],
    lons: list[float],
    lats: list[float],
    altis: list[float] = None,
    time_sleep: int = 10,
    dimension: int = 2,
    return_to_original: bool = True,
) -> list[dict[int, float]]:
    """
    ## Description:
        地理院APIでセミダイナミック補正を行うメイン処理
    Args:
        idxs(list[int]): インデックス
        correction_datetime(Union[str, int, datetime.datetime]): 補正日時
        lons(list[float]): 経度
        lats(list[float]): 緯度
        altis(list[float]): 標高
        time_sleep(int): 待ち時間。地理院APIのリクエスト制限による
        dimension(int): 2次元補正を行う場合は2、3次元補正を行う場合は3
        return_to_original(bool): Trueなら今期から元期に変換、Falseならば元期から今期へ変換
    Returns:
        list[dict[int, float]]: [{index: Coords}]
            - Coords: NamedTuple(longitude: float, latitude: float, altitude: float))
    """
    if altis is None:
        # 標高が指定されていない場合は、0.0mとする。問題はない
        altis = [0.0] * len(lons)

    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, lon, lat, alti in zip(idxs, lons, lats, altis, strict=False):
            task = fetch_corrected_semidynamic(
                session=session,
                index=idx,
                correction_datetime=correction_datetime,
                lon=lon,
                lat=lat,
                alti=alti,
                dimension=dimension,
                return_to_original=return_to_original,
            )
            tasks.append(task)
            if len(tasks) == 10:
                results += await asyncio.gather(*tasks)
                tasks = []
                time.sleep(time_sleep)
        if tasks:
            results += await asyncio.gather(*tasks)
    return results


def fetch_corrected_semidynamic_from_web(
    correction_datetime: Union[str, int, datetime.datetime],
    lons: list[float],
    lats: list[float],
    altis: list[float] = None,
    dimension: int = 2,
    return_to_original: bool = True,
) -> list[XYZ]:
    """
    ## Description:
        非同期処理により、地理院APIでセミダイナミック補正を行う。
        これは今期から元期への2次元補正を行う。2025/4以降に測量を行ったものでは
        通常2024年を元期とするが、2024年以前に測量を行ったものでは2011年を元期とする。
    Args:
        correction_datetime(Union[str, int, datetime.datetime]): 補正日時
        lons(list[float]): 10進経度
        lats(list[float]): 10進緯度
        altis(list[float]): 標高
        dimension(int): 2次元補正を行う場合は2、3次元補正を行う場合は3
        return_to_original(bool): Trueなら今期から元期に変換、Falseならば元期から今期へ変換
    Returns:
        list[Coords]: NamedTuple(longitude: float, latitude: float, altitude: float))
    """
    idxs = list(range(len(lons)))
    resps_lst = asyncio.run(
        fetch_corrected_semidynamic_main(
            idxs=idxs,
            correction_datetime=correction_datetime,
            lons=lons,
            lats=lats,
            altis=altis,
            dimension=dimension,
            return_to_original=return_to_original,
        )
    )
    _data = {}
    for resp in resps_lst:
        _data.update(resp)
    sorted_keys = sorted(_data.keys())
    sorted_coords = [_data[key] for key in sorted_keys]
    return sorted_coords


# ***********************************************************************
# **************** 地理院APIで距離と方位角を計算する ***********************
# ***********************************************************************


async def fetch_distance_and_azimuth(
    session: aiohttp.client.ClientSession,
    index: int,
    lon1: float,
    lat1: float,
    lon2: float,
    lat2: float,
    ellipsoid: str = "GRS80",
    max_retry: int = 5,
    time_out: int = 10,
) -> dict[int, tuple[float, float]]:
    """
    ## Description:
        地理院APIで2点間の距離と方位角を計算する
    Args:
        session(aiohttp.client.ClientSession): セッション
        index(int): インデックス
        lon1(float): 1点目の経度
        lat1(float): 1点目の緯度
        lon2(float): 2点目の経度
        lat2(float): 2点目の緯度
        ellipsoid(str): 楕円体。'GRS80'は世界測地系、'bessel'は日本測地系
        max_retry(int): リトライ回数
        time_out(int): タイムアウト
    Returns:
        dict[int, tuple[float, float]]: {index: (distance, azimuth)}
            - distance: 距離 (m)
            - azimuth: 方位角 (度)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
    }
    url = chiriin_web_api.distance_and_azimuth_url().format(
        ellipsoid=ellipsoid, lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2
    )
    for _ in range(max_retry):
        try:
            async with session.get(url, headers=headers, timeout=time_out) as response:
                data = await response.json()
                if data.get("ErrMsg") is None:
                    data = data.get("OutputData")
                    distance = float(data["geoLength"] if data['geoLength'] != '' else 0.0)
                    azimuth = float(data["azimuth1"] if data['azimuth1'] != '' else 0.0)
                    print(
                        f"Idx: {index}  距離: {distance}m, 方位角: {azimuth}度\n"
                        f"(lon1: {lon1}, lat1: {lat1}, lon2: {lon2}, lat2: {lat2})"
                    )
                    return {index: {"distance": distance, "azimuth": azimuth}}
                else:
                    print(f"サーバーが混みあっています。ErrMsg: {data.get('ErrMsg')}")
        except aiohttp.ClientError:
            print(
                f"リクエストに失敗しました (Index: {index}, lon1: {lon1}, lat1: {lat1}, "
                f"lon2: {lon2}, lat2: {lat2})。再試行中..."
            )
    return {index: None}


async def fetch_distance_and_azimuth_main(
    idxs: list[int],
    lons1: list[float],
    lats1: list[float],
    lons2: list[float],
    lats2: list[float],
    ellipsoid: str = "GRS80",
    time_sleep: int = 10,
) -> list[dict[int, tuple[float, float]]]:
    """
    ## Description:
        地理院APIで2点間の距離と方位角を計算するメイン処理
    Args:
        idxs(list[int]): インデックス
        lons1(list[float]): 1点目の経度
        lats1(list[float]): 1点目の緯度
        lons2(list[float]): 2点目の経度
        lats2(list[float]): 2点目の緯度
        ellipsoid(str): 楕円体。'GRS80'は世界測地系、'bessel'は日本測地系
        time_sleep(int): 待ち時間。地理院APIのリクエスト制限による
    Returns:
        list[dict[int, tuple[float, float]]]: [{index: (distance, azimuth)}]
            - distance: 距離 (m)
            - azimuth: 方位角 (度)
    """
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, lon1, lat1, lon2, lat2 in zip(
            idxs, lons1, lats1, lons2, lats2, strict=False
        ):
            task = fetch_distance_and_azimuth(
                session=session,
                index=idx,
                lon1=lon1,
                lat1=lat1,
                lon2=lon2,
                lat2=lat2,
                ellipsoid=ellipsoid,
            )
            tasks.append(task)
            if len(tasks) == 10:
                results += await asyncio.gather(*tasks)
                tasks = []
                time.sleep(time_sleep)
        if tasks:
            results += await asyncio.gather(*tasks)
    return results


def fetch_distance_and_azimuth_from_web(
    lons1: list[float],
    lats1: list[float],
    lons2: list[float],
    lats2: list[float],
    ellipsoid: str = "GRS80",
) -> list[tuple[float, float]]:
    """
    ## Description:
        非同期処理により、地理院APIで2点間の距離と方位角を計算する
    Args:
        lons1(list[float]): 1点目の10進経度
        lats1(list[float]): 1点目の10進緯度
        lons2(list[float]): 2点目の10進経度
        lats2(list[float]): 2点目の10進緯度
        ellipsoid(str): 楕円体。'GRS80'は世界測地系、'bessel'は日本測地系
    Returns:
        list[tuple[float, float]]: 距離と方位角のリスト [(distance, azimuth), ...]
            - distance: 距離 (m)
            - azimuth: 方位角 (度)
    """
    idxs = list(range(len(lons1)))
    resps_lst = asyncio.run(
        fetch_distance_and_azimuth_main(
            idxs=idxs,
            lons1=lons1,
            lats1=lats1,
            lons2=lons2,
            lats2=lats2,
            ellipsoid=ellipsoid,
        )
    )
    _data = {}
    for resp in resps_lst:
        _data.update(resp)
    sorted_keys = sorted(_data.keys())
    sorted_distance_azimuth = [_data[key] for key in sorted_keys]
    return sorted_distance_azimuth
