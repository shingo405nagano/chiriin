import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymupdf  # noqa: F401
import shapely  # noqa: F401
from matplotlib import pyplot as plt  # noqa: F401
from matplotlib.colors import to_hex  # noqa: F401
from shapely.geometry.base import BaseGeometry  # noqa: F401

from chiriin.config import XY, FigureSize, PaperSize, Scope  # noqa: F401
from chiriin.formatter import type_checker_float

paper_size = PaperSize()


class MapEditor(PaperSize):
    def __init__(
        self,
        geometry: BaseGeometry | list[BaseGeometry],
        in_crs: str = "EPSG:4326",
        paper_size: str = "portrait_a4",
        **kwargs,
    ):
        super().__init__()
        self.fig_size = self.get_parper_size(paper_size)
        self.fig, self.ax = self.make_sheet(paper_size)
        self.set_margin(
            self.fig_size,
            left_cm=kwargs.get("left_cm", 1.0),
            right_cm=kwargs.get("right_cm", 1.0),
            bottom_cm=kwargs.get("bottom_cm", 3.0),
            top_cm=kwargs.get("top_cm", 2.0),
        )

    def make_sheet(self, size: str = "portrait_a4") -> tuple[plt.Figure, plt.Axes]:
        """
        Create a sheet with the specified paper size.
        """
        fig_size = self.get_parper_size(size)
        # FigureとAxesを作成
        fig, ax = plt.subplots(figsize=fig_size)
        # 上下左右の余白を設定
        # 上下左右の余白をcm→inch変換して相対値で設定
        margin_cm = 1.0
        margin_inch = margin_cm / 2.54
        left = margin_inch / fig_size.width
        right = 1 - margin_inch / fig_size.width
        bottom = margin_inch / fig_size.height
        top = 1 - margin_inch / fig_size.height
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        return fig, ax

    def get_parper_size(self, size: str = "portrait_a4") -> FigureSize:
        """
        ## Summary:
            印刷用紙のサイズをインチ単位で取得する。戻り値のタプルは
            (幅, 高さ)の順で、matplotlibのfigsizeで使用できる。
        Args:
            size (str): 使用する紙のサイズ。'portrait_a4', 'landscape_a4',
                        'portrait_a3', 'landscape_a3'のいずれかを指定。
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
