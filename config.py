import datetime
import os
from glob import glob
from typing import NamedTuple, Optional

import pandas as pd

from chiriin.utils import datetime_formatter

# Load the mag data from a CSV file.
_mag_df = pd.read_csv(
    os.path.join(os.path.dirname(__file__), "chiriin", "data", "mag_2020.csv"),
    dtype={"mesh_code": int, "mag": float},
)
_mag_df["mesh_code"] = _mag_df["mesh_code"].astype(int).astype(str)
MAG_DATA: dict[int, float] = {
    mesh_code: mag_value for mesh_code, mag_value in zip(_mag_df["mesh_code"], _mag_df["mag"], strict=False)
}


FilePath = str


class XY(NamedTuple):
    """2次元座標を格納するクラス"""

    x: float
    y: float


class XYZ(NamedTuple):
    """3次元座標を格納するクラス"""

    x: float
    y: float
    z: float


class MeshDesign(NamedTuple):
    """ """

    name: str
    lon: float
    lat: float
    standard_mesh_code: str


class Delta(NamedTuple):
    """補正値を格納するクラス"""

    delta_x: float
    delta_y: float
    delta_z: float


class SemidynamicCorrectionFiles(object):
    def __init__(self):
        self.files = glob(os.path.join(os.path.dirname(__file__), "chiriin", "data", "*Semi*.par"))

    def _get_file_path(self, datetime_: datetime.datetime) -> FilePath:
        """
        ## Description:
            地殻変動補正のパラメーターファイルを探すクラス
        ## Args:
            datetime_ (datetime.datetime): 補正値を取得したい日時
        ## Returns:

        """
        datetime_ = datetime_formatter(datetime_)
        year = datetime_.year
        if datetime_.month < 4:
            # 年度の開始月が4月なので、1月から3月は前年のデータを使用
            year -= 1
        file_path = [file for file in self.files if str(year) in file][0]
        return file_path

    def _clean_line(self, line: list[str]) -> list[list[str]]:
        """
        ## Description:
            セミダイナミック補正のパラメータを読み込む際に、行ごとに読み込んでいるが
            その際に改行文字を削除し、数値に変換できるものは変換する為の関数。
        Args:
            line (list[str]):
                セミダイナミック補正のパラメータの行
        Returns:
            list[list[str]]:
                改行文字を削除し、数値に変換できるものは変換したリスト
        Example:
            >>> line = ['MeshCode', 'dB(sec)', '', 'dL(sec)', 'dH(m)\n']
            >>> xxx._clean_line(line)
            ['MeshCode', 'dB(sec)', 'dL(sec)', 'dH(m)']
            >>> line = ['36230600', '', '-0.05708', '', '', '0.04167', '', '', '0.05603\n']
            >>> xxx._clean_line(line)
            ['36230600', -0.05708, 0.04167, 0.05603]
        """
        result = []
        for txt in line:
            # 改行文字を削除
            txt = txt.replace("\n", "") if "\n" in txt else txt
            try:
                if "." in txt:
                    # 小数点が含まれている場合はfloatに変換
                    result.append(float(txt))
                else:
                    # 小数点が含まれていない場合はintに変換
                    result.append(int(txt))
            except Exception:
                # 変換できない場合はそのまま文字列として追加
                if txt == "":
                    # 空文字は無視
                    pass
                else:
                    result.append(txt)
        return result

    def read_file(self, datetime_: datetime.datetime, encoding: str = "utf-8") -> pd.DataFrame:
        """
        ## Description:
            地殻変動補正のパラメーターファイルを読み込む
        ## Args:
            datetime_ (datetime.datetime):
                補正値を取得したい日時
        ## Returns:
            pd.DataFrame:
                補正値のデータフレーム
        """
        file_path = self._get_file_path(datetime_)
        with open(file_path, mode="r", encoding=encoding) as f:
            # 16行目からパラメータが定義されている。
            lines = f.readlines()[15:]
            headers = self._clean_line(lines[0].split(" "))
            data = [self._clean_line(line.split(" ")) for line in lines[1:]]
            df = pd.DataFrame(data, columns=headers)
        # Breedte（緯度）Lengte（経度）
        df = df.rename(columns={"dB(sec)": "delta_y", "dL(sec)": "delta_x", "dH(m)": "delta_z"})
        return df.set_index("MeshCode")


def semidynamic_correction_file(datetime_: datetime.datetime) -> Optional[pd.DataFrame]:
    """
    ## Description:
        地殻変動補正のパラメーターファイルを読み込む
    ## Args:
        datetime_ (datetime.datetime):
            補正値を取得したい日時
    ## Returns:
        pd.DataFrame:
            補正値のデータフレーム。{index(int): MeshCode, columns: delta_x, delta_y, delta_z}
            補正値は秒単位の値なので、10進法で表現する時は3600で割る必要がある。
    ## Raises:
        RuntimeError:
            ファイルの読み込みに失敗した場合
        ValueError:
            すべてのエンコーディングでファイルの読み込みに失敗した場合
    """
    semi = SemidynamicCorrectionFiles()
    encodings = ["utf-8", "shift_jis", "cp932"]
    try:
        for encoding in encodings:
            try:
                return semi.read_file(datetime_, encoding=encoding)
            except UnicodeDecodeError:
                continue
    except Exception:
        raise ValueError("Failed to read the file with all encodings.use encofings: " + ", ".join(encodings))


class ChiriinWebApi(object):
    """
    ## Description:
        国土地理院の測量計算サイトで利用可能なAPIのURLを提供するクラス。
        ただし同一IPアドレスからのリクエストは、10秒間で10回までに制限されているため、
        連続してリクエストを送信する場合は注意が必要。
        https://vldb.gsi.go.jp/sokuchi/surveycalc/api_help.html
    """

    @staticmethod
    def elevation_url() -> str:
        """
        ## Description:
            地理院APIで標高値を取得するためのURL。
        ## Returns:
            str:
                地理院APIの標高値を取得するためのURL
        ## Example:
            >>> api = ChiriinWebApi()
            >>> url = api.elevation_url()
            >>> elev_url = url.format(lon=139.6917, lat=35.6895)
        """
        url = (
            "https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?"
            "outputtype=JSON&"
            "lon={lon}&"
            "lat={lat}"
        )
        return url

    @staticmethod
    def geoid_height_2011_url() -> str:
        """
        ## Description:
            地理院APIで2011年の日本の測地系におけるジオイド高を取得するためのURL。
        ## Returns:
            str:
                地理院APIのジオイド高を取得するためのURL
        """
        url = (
            "http://vldb.gsi.go.jp/sokuchi/surveycalc/geoid/calcgh2011/cgi/geoidcalc.pl?"
            "outputType=json&"
            "longitude={lon}&"
            "latitude={lat}"
        )
        return url

    @staticmethod
    def geoid_height_2024_url() -> str:
        """
        ## Description:
            地理院APIで2024年の日本の測地系におけるジオイド高を取得するためのURL。
        ## Returns:
            str:
                地理院APIのジオイド高を取得するためのURL
        """
        url = (
            "http://vldb.gsi.go.jp/sokuchi/surveycalc/geoid/calcgh/cgi/geoidcalc.pl?"
            "outputType=json&"
            "longitude={lon}&"
            "latitude={lat}"
        )
        return url

    @staticmethod
    def distance_and_azimuth_url() -> str:
        """
        ## Description:
            地理院APIで2点間の距離と方位角を取得するためのURL。
        ## Returns:
            str:
                地理院APIの距離と方位角を取得するためのURL
                ellipsoidは、'GRS80'は世界測地系で計算する。'bessel'は日本測地系で計算する。
        """
        url = (
            "http://vldb.gsi.go.jp/sokuchi/surveycalc/surveycalc/bl2st_calc.pl?"
            "outputType=json&"
            "ellipsoid={ellipsoid}"
            "longitude1={lon1}"
            "latitude1={lat1}"
            "longitude2={lon2}"
            "latitude2={lat2}"
        )
        return url

    @staticmethod
    def semidynamic_correction_url() -> str:
        """
        ## Description:
            地理院APIでセミダイナミック補正を行う為のURL。
        ## Returns:
            str:
                地理院APIのセミダイナミック補正を行う為のURL
        """
        url = (
            "http://vldb.gsi.go.jp/sokuchi/surveycalc/semidyna/web/semidyna_r.php?"
            "outputType=json&"
            "chiiki=SemiDyna{year}.par&"  # パラメーターファイル名（.par）
            "sokuchi={sokuchi}&"  # 0: 元期 -> 今期, 1: 今期 -> 元期
            "Place=0&"
            "Hosei_J={dimension}&"  # 2: 2次元補正, 3: 3次元補正
            "longitude={lon}&"
            "latitude={lat}&"
            "altitude1={alti}&"
        )
        return url
