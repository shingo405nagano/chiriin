import datetime
from decimal import Decimal
from typing import Iterable, Optional, Union

import pandas as pd

from chiriin.config import XY, Delta, MeshDesign, semidynamic_correction_file
from chiriin.formatter import (
    datetime_formatter,
    iterable_decimalize_formatter,
    type_checker_decimal,
)
from chiriin.mesh import MeshCode
from chiriin.utils import dimensional_count


class SemiDynamic(object):
    def __init__(
        self,
        lon: float | Iterable[float],
        lat: float | Iterable[float],
        datetime_: Union[datetime.datetime, Iterable[datetime.datetime]],
        altitude: Optional[float | Iterable[float]] = None,
        is_dms: bool = False,
    ):
        self.lon = lon
        self.lat = lat
        self.altitude = altitude
        self.datetime = datetime_formatter(datetime_)
        self._is_dms = is_dms
        self._is_iterable = False
        # Convert longitude and latitude to float or iterable of floats
        self._convert_lon_lat()
        self._param_df = self._read_parameters()

    def _convert_lon_lat(self):
        """
        ## Description:
            Convert longitude and latitude values to DecimalObject or
            iterable of DecimalObject.
        """
        count_lon = dimensional_count(self.lon)
        count_lat = dimensional_count(self.lat)
        assert count_lon == count_lat, "longitude and latitude must have the same dimensionality."
        if count_lon == 0:
            self.lon = Decimal(f"{float(self.lon)}")
            self.lat = Decimal(f"{float(self.lat)}")
            if self.altitude is not None:
                self.altitude = Decimal(f"{float(self.altitude)}")
        else:
            self.lon = iterable_decimalize_formatter(self.lon)
            self.lat = iterable_decimalize_formatter(self.lat)
            if self.altitude is not None:
                self.altitude = iterable_decimalize_formatter(self.altitude)
            self._is_iterable = True

    def _read_parameters(self) -> pd.DataFrame:
        """
        ## Description:
            Read the semi-dynamic correction parameters from a file based on the datetime.
        ## Returns:
            pd.DataFrame:
                Index: Mesh code(int)
                Columns: delta_x(float), delta_y(float), delta_z(float)
            'delta' is DMS float format.
        """
        return semidynamic_correction_file(self.datetime)

    @type_checker_decimal(arg_index=1, kward="lon")
    @type_checker_decimal(arg_index=2, kward="lat")
    def mesh_design(self, lon: float, lat: float) -> dict[str, MeshDesign]:
        """
        ## Description:
            Generate mesh designs for the given longitude and latitude.
        ## Args:
            lon (Decimal):
                Longitude in degrees.
            lat (Decimal):
                Latitude in degrees.
        ## Returns:
            dict[str, MeshDesign] | list[MeshDesign]:
                A dictionary containing mesh designs for the four corners of the mesh.
                Mesh designs include:
                - lower_left: MeshDesign for the lower left corner
                - lower_right: MeshDesign for the lower right corner
                - upper_left: MeshDesign for the upper left corner
                - upper_right: MeshDesign for the upper right corner
            MeshDesign:
                - name: Name of the mesh corner (e.g., 'lower_left')
                - lon: Longitude in seconds
                - lat: Latitude in seconds
                - standard_mesh_code: Standard mesh code for the corner
        """
        lon_param = 225
        lat_param = 150
        lower_left_sec_lon = round(lon * 3600, 1)
        lower_left_sec_lat = round(lat * 3600, 1)
        m = int(lower_left_sec_lon / lon_param)
        n = int(lower_left_sec_lat / lat_param)
        lower_left_sec_lon = m * lon_param
        lower_left_sec_lat = n * lat_param
        lower_left_deg_lon = lower_left_sec_lon / 3600
        lower_left_deg_lat = lower_left_sec_lat / 3600
        try:
            # Create MeshCode and MeshDesign for lower left corner
            lower_left_mesh_code = MeshCode(lower_left_deg_lon, lower_left_deg_lat)
            lower_left_design = MeshDesign(
                "lower_left",
                lower_left_sec_lon,
                lower_left_sec_lat,
                lower_left_mesh_code.standard_mesh_code,
            )
            lower_right_design = self._adjust_mesh_code(
                lower_left_sec_lon, lower_left_sec_lat, lon_param, 0, "lower_right"
            )
            upper_left_design = self._adjust_mesh_code(
                lower_left_sec_lon, lower_left_sec_lat, 0, lat_param, "upper_left"
            )
            upper_right_design = self._adjust_mesh_code(
                lower_left_sec_lon,
                lower_left_sec_lat,
                lon_param,
                lat_param,
                "upper_right",
            )
        except Exception:
            return False
        else:
            return {
                "lower_left": lower_left_design,
                "lower_right": lower_right_design,
                "upper_left": upper_left_design,
                "upper_right": upper_right_design,
            }

    def _adjust_mesh_code(
        self,
        lower_left_sec_lon: float,
        lower_left_sec_lat,
        lon_param: int = 225,
        lat_param: int = 150,
        name: str = "lower_right",
    ) -> MeshDesign:
        """
        ## Description:
            Adjust the mesh code from the longitude and latitude in seconds.
        Args:
            lower_left_sec_lon (float): Longitude (in seconds) at lower left
            lower_left_sec_lat (float): Latitude (in seconds) at lower left
            lon_param (int, optional): Longitude parameter.Default is 225.
            lat_param (int, optional): Latitude parameter. Default is 150.
            name (str, optional): Name of the mesh corner. Default is "lower_right".
        Returns:
            MeshDesign:
                - name: Name of the mesh corner
                - lon: Longitude in seconds
                - lat: Latitude in seconds
                - standard_mesh_code: Standard mesh code for the corner
        """
        sec_lon = lower_left_sec_lon + lon_param
        sec_lat = lower_left_sec_lat + lat_param
        mesh_code = MeshCode(sec_lon / 3600, sec_lat / 3600)
        return MeshDesign(
            name=name,
            lon=sec_lon,
            lat=sec_lat,
            standard_mesh_code=mesh_code.standard_mesh_code,
        )

    def _get_delta_sets(self, mesh_designs: dict[str, MeshDesign]) -> dict[str, Delta]:
        """
        ## Description:
            Obtain Delta in 4 directions from the parameters of the semi-dynamic correction.
        Args:
            mesh_designs (dict[str, MeshDesign]):
                Dictionaries containing mesh designs for the four corners of the mesh.
        Returns:
            DeltaSet:
                DeltaSet object containing Delta in 4 directions.
        """
        lower_left_delta = self._get_delta(mesh_designs["lower_left"].standard_mesh_code)
        lower_right_delta = self._get_delta(mesh_designs["lower_right"].standard_mesh_code)
        upper_left_delta = self._get_delta(mesh_designs["upper_left"].standard_mesh_code)
        upper_right_delta = self._get_delta(mesh_designs["upper_right"].standard_mesh_code)
        return {
            "lower_left": lower_left_delta,
            "lower_right": lower_right_delta,
            "upper_left": upper_left_delta,
            "upper_right": upper_right_delta,
        }

    def _get_delta(self, mesh_code: str) -> Delta:
        """
        ## Description:
            Obtain Delta from the parameters of the semi-dynamic correction.
        Args:
            param_df (pd.DataFrame):
                DataFrame containing parameters for semi-dynamic correction
            mesh_code (str):
                mesh cord
        Returns:
            Delta:
                - delta_x(Decimal): Correction value for x-coordinate
                - delta_y(Decimal): Correction value for y-coordinate
                - delta_z(Decimal): Correction value for z-coordinate
        """
        try:
            row = self._param_df.loc[int(mesh_code)]
        except KeyError:
            raise KeyError(f"Mesh code {mesh_code} not found in parameters.")  # noqa: B904
        return Delta(
            delta_x=Decimal(f"{row['delta_x']}"),
            delta_y=Decimal(f"{row['delta_y']}"),
            delta_z=Decimal(f"{row['delta_z']}"),
        )

    @type_checker_decimal(arg_index=1, kward="lon")
    @type_checker_decimal(arg_index=2, kward="lat")
    def _calc_correction_2d_delta(self, lon: float, lat: float, return_to_original: bool = True) -> XY:
        """
        ## Description:
            経緯度（10進法）を受け取り、セミダイナミック補正を行う。
        Args:
            lon (float):
                ターゲットの経度（10進法）
            lat (float):
                ターゲットの緯度（10進法）
            return_to_original (bool, optional):
                Trueは今期から元期への補正を行う。Falseは元期から今期への補正を行う。
        Returns:
            dict[str, float]:
                補正後の経度と緯度を含む辞書。
                {'lon': 経度, 'lat': 緯度}
        """
        mesh_designs = self.mesh_design(lon, lat)
        if not mesh_designs:
            return {"lon": False, "lat": False}
        # 経度と緯度を秒単位に変換
        lon = lon * 3600
        lat = lat * 3600
        # MeshDesign(name, lon, lat, standard_mesh_code)
        lower_left_design = mesh_designs["lower_left"]
        lower_right_design = mesh_designs["lower_right"]
        upper_left_design = mesh_designs["upper_left"]
        # Delta(delta_x, delta_y, delta_z)
        delta_sets = self._get_delta_sets(mesh_designs)
        lower_left_delta = delta_sets["lower_left"]
        lower_right_delta = delta_sets["lower_right"]
        upper_left_delta = delta_sets["upper_left"]
        upper_right_delta = delta_sets["upper_right"]
        # バイリニア補間により補正値を計算
        x_norm = (lon - lower_left_design.lon) / (lower_right_design.lon - lower_left_design.lon)
        y_norm = (lat - lower_left_design.lat) / (upper_left_design.lat - lower_left_design.lat)
        delta_lon_p = (
            (1 - y_norm) * (1 - x_norm) * lower_left_delta.delta_x
            + y_norm * (1 - x_norm) * lower_right_delta.delta_x
            + y_norm * x_norm * upper_right_delta.delta_x
            + (1 - y_norm) * x_norm * upper_left_delta.delta_x
        )
        delta_lat_p = (
            (1 - y_norm) * (1 - x_norm) * lower_left_delta.delta_y
            + y_norm * (1 - x_norm) * lower_right_delta.delta_y
            + y_norm * x_norm * upper_right_delta.delta_y
            + (1 - y_norm) * x_norm * upper_left_delta.delta_y
        )
        # 元期から今期へのパラメーターなので、今期から元期へは -1 を掛ける
        if return_to_original:
            delta_lon_p *= -1
            delta_lat_p *= -1
        return Delta(delta_x=delta_lon_p, delta_y=delta_lat_p, delta_z=0)

    def correction_2d(self, return_to_original: bool = True) -> XY | list[XY]:
        """
        ## Description:
            Receives longitude and latitude (decimal system) and performs semi-dynamic correction.
        Args:
            return_to_original (bool, optional):
                True makes a correction from the current period to the previous period.
                False makes a correction from the previous period to the current period.
        Returns:
        """
        if not self._is_iterable:
            delta = self._calc_correction_2d_delta(self.lon, self.lat, return_to_original)
            corrected_lon = float(self.lon + (delta.delta_x / 3600))
            corrected_lat = float(self.lat + (delta.delta_y / 3600))
            return XY(x=corrected_lon, y=corrected_lat)
        # If the input is iterable, apply the correction to each element
        lst = []
        previous_mesh_code = None
        for lon, lat in zip(self.lon, self.lat, strict=True):
            mesh_code = MeshCode(float(lon), float(lat)).standard_mesh_code
            if mesh_code is None:
                delta = self._calc_correction_2d_delta(lon, lat, return_to_original)
                previous_mesh_code = mesh_code
            elif mesh_code != previous_mesh_code:
                delta = self._calc_correction_2d_delta(lon, lat, return_to_original)
                previous_mesh_code = mesh_code
            corrected_lon = lon + (delta.delta_x / 3600)
            corrected_lat = lat + (delta.delta_y / 3600)
            lst.append(XY(x=float(corrected_lon), y=float(corrected_lat)))
        return lst
