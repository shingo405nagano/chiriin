import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymupdf  # noqa: F401
import pyproj
import shapely  # noqa: F401
from matplotlib import pyplot as plt
from matplotlib.colors import to_hex  # noqa: F401
from shapely.geometry.base import BaseGeometry

from chiriin.config import XY, FigureSize, PaperSize, Scope  # noqa: F401
from chiriin.formatter import type_checker_crs, type_checker_float
from chiriin.geometries import estimate_utm_crs, transform_geometry
from chiriin.utils import dimensional_count

paper_size = PaperSize()


class MapEditor(PaperSize):
    def __init__(
        self,
        geometry: BaseGeometry | list[BaseGeometry],
        in_crs: str | int | pyproj.CRS = "EPSG:4326",
        out_crs: Optional[str | int | pyproj.CRS] = None,
        paper_size: str = "portrait_a4",
        **kwargs,
    ):
        super().__init__()
        self._is_iterable = False
        self.fig_size = self.get_parper_size(paper_size)
        self.fig, self.ax = self.make_sheet(paper_size)
        # 余白を設定
        left_cm = kwargs.get("left_cm", 1.0)
        right_cm = kwargs.get("right_cm", 1.0)
        bottom_cm = kwargs.get("bottom_cm", 3.0)
        top_cm = kwargs.get("top_cm", 2.0)
        self.set_margin(self.fig_size, left_cm, right_cm, bottom_cm, top_cm)
        # 実際に使用する部分のサイズを計算
        self.map_width = round(self.fig_size.width * 2.54 - (left_cm + right_cm), 2)
        self.map_height = round(self.fig_size.height * 2.54 - (bottom_cm + top_cm), 2)
        # geometryをmetre単位に変換
        self.org_geometry = geometry
        self.metre_geometry = self._transform_geometry(
            geometry=geometry,
            in_crs=in_crs,
            out_crs=out_crs,
        )
        # ``geometry``の範囲を取得
        if self._is_iterable:
            self.scope = Scope(*shapely.union_all(self.metre_geometry).bounds)
        else:
            self.scope = Scope(*self.metre_geometry.bounds)
        # 投影可能な縮尺を計算
        self.valid_scales = self._valid_scales()

    def make_sheet(self, size: str = "portrait_a4") -> tuple[plt.Figure, plt.Axes]:
        """
        ## Summary:
            matplotlibのFigureとAxesを作成する。
        Args:
            size (str):
                使用する紙のサイズ。
                - 'portrait_a4'
                - 'landscape_a4',
                - 'portrait_a3'
                - 'landscape_a3'
        Returns:
            tuple[plt.Figure, plt.Axes]:
                作成されたFigureとAxesのタプル。
        """
        fig_size = self.get_parper_size(size)
        # FigureとAxesを作成
        fig, ax = plt.subplots(figsize=fig_size)
        return fig, ax

    def get_parper_size(self, size: str = "portrait_a4") -> FigureSize:
        """
        ## Summary:
            印刷用紙のサイズをインチ単位で取得する。戻り値のタプルは
            (幅, 高さ)の順で、matplotlibのfigsizeで使用できる。
        Args:
            size (str):
                使用する紙のサイズ。
                - 'portrait_a4'
                - 'landscape_a4'
                - 'portrait_a3'
                - 'landscape_a3'
        Returns:
            FigureSize:
                A4用紙の縦向きのサイズを計算したタプル。
                幅と高さをmatplotlibのFigureオブジェクトとして設定できるタプル。
                - width (float): 幅（インチ単位）
                - height (float): 高さ（インチ単位）
        """
        ps = {
            "portrait_a4": paper_size.portrait_a4_size(),
            "landscape_a4": paper_size.landscape_a4_size(),
            "portrait_a3": paper_size.portrait_a3_size(),
            "landscape_a3": paper_size.landscape_a3_size(),
        }.get(size, None)
        if ps is None:
            raise ValueError(
                f"Invalid paper size: {size}. Choose from 'portrait_a4', 'lands"
                "cape_a4', 'portrait_a3', 'landscape_a3'."
            )
        return ps

    @type_checker_float(arg_index=2, kward="left_cm")
    @type_checker_float(arg_index=3, kward="right_cm")
    @type_checker_float(arg_index=4, kward="bottom_cm")
    @type_checker_float(arg_index=5, kward="top_cm")
    def set_margin(
        self,
        figsize: FigureSize,
        left_cm: float,
        right_cm: float,
        bottom_cm: float,
        top_cm: float,
    ) -> None:
        """
        ## Summary:
            用紙の余白を設定する。
        Args:
            figsize (FigureSize): matplotlibのFigureオブジェクトのサイズ。
            left_cm (float): 左余白の幅（センチメートル単位）。
            right_cm (float): 右余白の幅（センチメートル単位）。
            bottom_cm (float): 下余白の高さ（センチメートル単位）。
            top_cm (float): 上余白の高さ（センチメートル単位）。
        Returns:
            None
        """
        # センチメートルからインチに変換
        left_inch = left_cm / 2.54
        right_inch = right_cm / 2.54
        bottom_inch = bottom_cm / 2.54
        top_inch = top_cm / 2.54
        # 余白を計算
        left = left_inch / figsize.width
        right = 1 - right_inch / figsize.width
        bottom = bottom_inch / figsize.height
        top = 1 - top_inch / figsize.height
        self.fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)

    def _calc_valid_scales(self) -> dict[int, Scope]:
        """
        ## Summary:
            投影可能な縮尺を計算する。
        Returns:
            dict[int, Scope]:
                投影可能な縮尺とその範囲を表す辞書。
                キーは縮尺(int)で、値は``Scope``オブジェクト。
        """
        # 100mが何センチメートルかを計算
        valid_scales = {}
        scales = []
        scales += list(range(1_000, 5_500, 500))
        scales += list(range(6_000, 11_000, 1_000))
        scales += list(range(10_000, 55_000, 5_000))
        scales += list(range(60_000, 110_000, 10_000))
        for scale in scales:
            # 1cmあたりのメートル数を計算
            unit = scale / 100.0
            # geometryの範囲を取得
            geom_width = self.scope.x_max - self.scope.x_min
            geom_height = self.scope.y_max - self.scope.y_min
            # geometry が設定された範囲に収まるかを確認
            checked_width = geom_width <= unit * self.map_width
            checked_height = geom_height <= unit * self.map_height
            if checked_width and checked_height:
                # 有効な縮尺ならば、geometry.boundsの中心を取得し、マップ範囲を計算する
                pnt = shapely.box(*self.scope).centroid
                x_unit = unit * self.map_width / 2
                y_unit = unit * self.map_height / 2
                x_min = pnt.x + x_unit * -1
                x_max = pnt.x + x_unit
                y_min = pnt.y + y_unit * -1
                y_max = pnt.y + y_unit
                scope = Scope(*[round(v, 2) for v in [x_min, y_min, x_max, y_max]])
                try:
                    assert scope.x_min <= self.scope.x_min
                    assert self.scope.x_max <= scope.x_max
                    assert scope.y_min <= self.scope.y_min
                    assert self.scope.y_max <= scope.y_max
                except AssertionError:
                    # geometryの範囲が設定された範囲に収まらない場合はスキップ
                    continue
                else:
                    valid_scales[scale] = scope
        return valid_scales

    @type_checker_crs(arg_index=2, kward="in_crs")
    def _transform_geometry(
        self,
        geometry: BaseGeometry | list[BaseGeometry],
        in_crs: str | int | pyproj.CRS,
        out_crs: Optional[pyproj.CRS] = None,
        datum_name: str = "JGD2011",
    ) -> BaseGeometry | list[BaseGeometry]:
        """
        ## Summary:
            入力されたCRSから出力CRSに変換する。
        Args:
            in_crs (str | int | pyproj.CRS):
                ``geometry``のCRS。
            out_crs (Optional[str | int | pyproj.CRS]):
                出力CRS。指定しない場合はUTM座標系を推定する。
        Returns:
            BaseGeometry | list[BaseGeometry]:
                変換後のジオメトリ。
        """
        # CRSをメートル単位に変換
        if out_crs is None:
            pnt = geometry.centroid
            out_crs = estimate_utm_crs(pnt.x, pnt.y, datum_name)
        # 次元数を数える
        dim_count = dimensional_count(geometry)
        if dim_count == 0:
            # ジオメトリが単一のジオメトリの場合
            geom = transform_geometry(
                geometry=geometry,
                in_crs=in_crs,
                out_crs=out_crs,
            )
            self._is_iterable = False
            return geom
        elif dim_count == 1:
            # ジオメトリが複数のジオメトリの場合
            geom_list = []
            for geom in geometry:
                geom = transform_geometry(
                    geometry=geom,
                    in_crs=in_crs,
                    out_crs=out_crs,
                )
                geom_list.append(geom)
            self._is_iterable = True
            return geom_list
        else:
            raise ValueError(
                "Geometry must be a Point, LineString, Polygon, or Multi* type."
                f"The number of dimensions sought is 0, 1. Received {dim_count} "
                "dimensions."
            )
