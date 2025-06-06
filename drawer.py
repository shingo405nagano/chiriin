"""
参考情報：
[地域メッシュ統計の特質・沿革](https://www.stat.go.jp/data/mesh/pdf/gaiyo1.pdf)
[セミダイナミック補正マニュアル](https://www.gsi.go.jp/common/000258815.pdf)
[セミダイナミック補正のパラメーターファイル](https://www.gsi.go.jp/sokuchikijun/semidyna.html)
[高精度衛星測位システムの開発](https://kagoshima.daiichi-koudai.ac.jp/wp-content/uploads/2023/07/R5_report1_11.pdf)
[磁気図](https://www.gsi.go.jp/buturisokuchi/menu03_magnetic_chart.html)
[測量計算サイト](https://vldb.gsi.go.jp/sokuchi/surveycalc/api_help.html)
[標高タイルURL](https://maps.gsi.go.jp/development/ichiran.html#dem-1)
[標高タイルの詳細](https://maps.gsi.go.jp/development/demtile.html)
"""

import datetime
from typing import Iterable

from chiriin.config import XY, XYZ, RelativePosition
from chiriin.formatter import type_checker_iterable
from chiriin.mag import get_magnetic_declination
from chiriin.mesh import MeshCode
from chiriin.semidynamic import SemiDynamic
from chiriin.web import fetch_distance_and_azimuth_from_web


class _ChiriinDrawer(object):
    @staticmethod
    def magnetic_declination(lon: float, lat: float, is_dms: bool = False) -> float:
        """
        ## Summary:
            国土地理院の公開している地磁気値（2020.0年値）のパラメーターファイルを
            用いて、任意の地点の地磁気偏角を計算します。この地磁気値は通常5年ごとに
            更新されるので、最新の値を使用することをお勧めします。
            [磁器図](https://www.gsi.go.jp/buturisokuchi/menu03_magnetic_chart.html)
        Args:
            lon (float):
                経度（10進法） or 度分秒形式
            lat (float):
                緯度（10進法）or 度分秒形式
            is_dms (bool):
                経緯度が度分秒形式かどうか
        Returns:
            float:
                地磁気偏角（度）
        """
        return get_magnetic_declination(lon, lat, is_dms)

    @staticmethod
    def get_mesh_code(lon: float, lat: float, is_dms: bool = False) -> MeshCode:
        """
        ## Summary:
            任意の地点のメッシュコードを取得します。
            経緯度が度分秒形式の場合は、10進法に変換してから計算します。
            地域メッシュコードの計算方法は、総務省が公開しているPDFファイルを
            参照しています。
            [地域メッシュ統計の特質・沿革](https://www.stat.go.jp/data/mesh/pdf/gaiyo1.pdf)
        Args:
            lon (float):
                経度（10進法） or 度分秒形式
            lat (float):
                緯度（10進法）or 度分秒形式
            is_dms (bool):
                経緯度が度分秒形式かどうか
        Returns:
            MeshCode:
                メッシュコードの各部分を含むMeshCodeオブジェクト
                - first_mesh_code: 第1次メッシュコード
                - secandary_mesh_code: 第2次メッシュコード
                - standard_mesh_code: 基準地域メッシュコード
                - half_mesh_code: 2分の1地域メッシュコード
                - quarter_mesh_code: 4分の1地域メッシュコード
        """
        return MeshCode(lon, lat, is_dms)

    @staticmethod
    def semidynamic_2d(
        lon: float | Iterable[float],
        lat: float | Iterable[float],
        datetime_: datetime.datetime,
        return_to_original: bool = True,
    ) -> XY | list[XY]:
        """
        ## Summary:
            セミダイナミック補正による2次元の地殻変動補正を行い、補正後の座標を
            返すメソッドです。補正には「今期から元期へ」と「元期から今期へ」の変
            換があり、それぞれパラメーターファイルを取得する為に座標の計測日が必
            要です。
        Args:
            lon (float | Iterable[float]):
                経度（10進法）の数値またはリストなどの反復可能なオブジェクト
            lat (float | Iterable[float]):
                緯度（10進法）の数値またはリストなどの反復可能なオブジェクト
            datetime_ (datetime.datetime):
                座標の計測日時。この日時によって使用するパラメーターファイルが
                決まります。
            return_to_original (bool):
                True: 「今期から元期へ」の補正を行い、補正後の座標を返す
                False: 「元期から今期へ」の補正を行い、補正後の座標を返す
        """
        semidynamic = SemiDynamic(
            lon=lon,
            lat=lat,
            datetime_=datetime_,
        )
        return semidynamic.correction_2d(return_to_original)

    @staticmethod
    def semidynamic_2d_with_web_api(
        lon: float | Iterable[float],
        lat: float | Iterable[float],
        datetime_: datetime.datetime,
        return_to_original: bool = True,
    ) -> XY | list[XY]:
        """
        ## Summary:
            セミダイナミック補正による2次元の地殻変動補正を行い、補正後の座標を
            返すメソッドです。補正には「今期から元期へ」と「元期から今期へ」の
            変換があり、それぞれパラメーターファイルを取得する為に座標の計測日が
            必要です。
            通常のセミダイナミック補正メソッド（`semidynamic_2d`）とは異なり、こ
            のメソッドは国土地理院の公開しているWeb APIを使用して、セミダイナミ
            ック補正を行います。その為、API利用制限があり10秒間に10回のリクエス
            トに制限しています。
        Args:
            lon (float | Iterable[float]):
                経度（10進法）の数値またはリストなどの反復可能なオブジェクト
            lat (float | Iterable[float]):
                緯度（10進法）の数値またはリストなどの反復可能なオブジェクト
            datetime_ (datetime.datetime):
                座標の計測日時。この日時によって使用するパラメーターファイルが
                決まります。
            return_to_original (bool):
                True: 「今期から元期へ」の補正を行い、補正後の座標を返す
                False: 「元期から今期へ」の補正を行い、補正後の座標を返す
        """
        semidynamic = SemiDynamic(
            lon=lon,
            lat=lat,
            datetime_=datetime_,
        )
        return semidynamic.correction_2d_with_web_api(return_to_original)

    @staticmethod
    def semidynamic_3d_with_web_api(
        lon: float | Iterable[float],
        lat: float | Iterable[float],
        altitude: float | Iterable[float],
        datetime_: datetime.datetime,
        return_to_original: bool = True,
    ) -> XYZ | list[XYZ]:
        """
        ## Summary:
            セミダイナミック補正による3次元の地殻変動補正を行い、補正後の座標を
            返すメソッドです。補正には「今期から元期へ」と「元期から今期へ」の
            変換があり、それぞれパラメーターファイルを取得する為に座標の計測日が
            必要です。
            通常のセミダイナミック補正メソッド（`semidynamic_3d`）とは異なり、この
            メソッドは国土地理院の公開しているWeb APIを使用して、セミダイナミッ
            ク補正を行います。その為、API利用制限があり10秒間に10回のリクエス
            トに制限しています。
        Args:
            lon (float | Iterable[float]):
                経度（10進法）の数値またはリストなどの反復可能なオブジェクト
            lat (float | Iterable[float]):
                緯度（10進法）の数値またはリストなどの反復可能なオブジェクト
            altitude (float | Iterable[float]):
                標高（メートル単位）の数値またはリストなどの反復可能なオブジェクト
            datetime_ (datetime.datetime):
                座標の計測日時。この日時によって使用するパラメーターファイルが
                決まります。
            return_to_original (bool):
                True: 「今期から元期へ」の補正を行い、補正後の座標を返す
                False: 「元期から今期へ」の補正を行い、補正後の座標を返す
        """
        semidynamic = SemiDynamic(
            lon=lon,
            lat=lat,
            altitude=altitude,
            datetime_=datetime_,
        )
        return semidynamic.correction_3d_with_web_api(return_to_original)

    @staticmethod
    @type_checker_iterable(arg_index=0, kward="lon1")
    @type_checker_iterable(arg_index=1, kward="lat1")
    @type_checker_iterable(arg_index=2, kward="lon2")
    @type_checker_iterable(arg_index=3, kward="lat2")
    def distance_and_azimuth_with_web_api(
        lon1: float | Iterable[float],
        lat1: float | Iterable[float],
        lon2: float | Iterable[float],
        lat2: float | Iterable[float],
        ellipsoid: str = "bessel",
    ) -> RelativePosition | list[RelativePosition]:
        """
        ## Summary:
            2点間の距離と方位角を計算するメソッドです。
            国土地理院の公開しているWeb APIを使用して、距離と方位角を計算します。
            このメソッドは、10秒間に10回のリクエスト制限があります。
        Args:
            lon1 (float | Iterable[float]):
                1点目の経度（10進法）の数値またはリストなどの反復可能なオブジェクト
            lat1 (float | Iterable[float]):
                1点目の緯度（10進法）の数値またはリストなどの反復可能なオブジェクト
            lon2 (float | Iterable[float]):
                2点目の経度（10進法）の数値またはリストなどの反復可能なオブジェクト
            lat2 (float | Iterable[float]):
                2点目の緯度（10進法）の数値またはリストなどの反復可能なオブジェクト
            ellipsoid (str):
                計算に使用する楕円体。'GRS80'は世界測地系で計算する。'bessel'は日本測地系で計算する。
        Returns:
            RelativePosition | list[RelativePosition]:
                距離と方位角を含むRelativePositionオブジェクトまたはそのリスト
                - xyz1: 1点目の座標（XYオブジェクト）
                - xyz2: 2点目の座標（XYオブジェクト）
                - azimuth: 方位角（度）
                - level_distance: 水平距離（メートル）
                - angle: 高度角（度）
                - slope_distance: 斜距離（メートル）
        """
        resps = fetch_distance_and_azimuth_from_web(
            lons1=lon1,
            lats1=lat1,
            lons2=lon2,
            lats2=lat2,
            ellipsoid=ellipsoid,
        )
        relative_objs = []
        for data, lon1_, lat1_, lon2_, lat2_ in zip(
            resps, lon1, lat1, lon2, lat2, strict=False
        ):
            xy1 = XY(lon1_, lat1_)
            xy2 = XY(lon2_, lat2_)
            relative_obj = RelativePosition(
                xyz1=xy1,
                xyz2=xy2,
                azimuth=data["azimuth"],
                level_distance=data["distance"],
                angle=0.0,
                slope_distance=0.0,
            )
            relative_objs.append(relative_obj)
        if len(relative_objs) == 1:
            return relative_objs[0]
        return relative_objs


# 通常はこのモジュールをインポートするだけで
# _ChiriinDrawer クラスのメソッドを使用できます。
chiriin_drawer = _ChiriinDrawer()
