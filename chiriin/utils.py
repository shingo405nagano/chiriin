import datetime
from typing import Union

import numpy as np
import pandas as pd

UniqueIterable = Union[tuple, list, np.ndarray, pd.Series]


def datetime_formatter(dt: datetime.datetime | str) -> datetime.datetime:
    """
    ## Description:
        日時のフォーマットを統一する関数
        datetimeオブジェクトまたは文字列を受け取り、マイクロ秒を0にして返す
    ## Args:
        dt (datetime.datetime | str): 日時を表すdatetimeオブジェクトまたは文字列
    ## Returns:
        datetime.datetime: マイクロ秒が0に設定されたdatetimeオブジェクト
    """
    fmts = [
        # データがこのフォーマットに合致するかチェック
        # 変換でエラーが生じた場合は、このフォーマットに新しく追加する
        # 2023-11-16T11:06:21.700+09:00
        "%Y-%m-%dT%H:%M:%S.%f+%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ]
    if isinstance(dt, datetime.datetime):
        return dt.replace(microsecond=0)
    elif isinstance(dt, str):
        for fmt in fmts:
            # 各フォーマットで変換を試みる
            try:
                return datetime.datetime.strptime(dt, fmt).replace(microsecond=0)
            except Exception:
                continue
        try:
            return datetime.datetime.fromisoformat(dt).replace(tzinfo=None, microsecond=0)
        except Exception:
            raise ValueError(f"Unsupported datetime format: {dt}")  # noqa: B904
    raise TypeError(f"Expected datetime or str, got {type(dt)}")


def dimensional_count(value: UniqueIterable) -> int:
    """
    ## Description:
        Recursively determine the dimensionality of a list.
    Arguments:
        value (tuple | list | np.ndarray | pd.Series):
            The list to be measured.
    Returns:
        int: The dimensionality of the list.
            - 0: The value is not a list. (str, int, float, etc.)
            - 1: The value is a list.
            - 2: The value is a list of lists.
            - 3: The value is a list of lists of lists.
            - ...
    Examples:
        >>> dimensional_measurement(1)
        0
        >>> dimensional_measurement('a')
        0
        >>> dimensional_measurement([1, 2, 3])
        1
        >>> dimensional_measurement([[1, 2, 3], [4, 5, 6]])
        2
        >>> dimensional_measurement([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]])
        3
    """
    if isinstance(value, UniqueIterable):
        try:
            # Convert numpy arrays to lists
            value = value.tolist()  # type: ignore
        except:  # noqa: E722
            try:
                # Convert pandas Series to lists
                value = value.to_list()  # type: ignore
            except:  # noqa: E722
                pass
        return 1 + max(dimensional_count(item) for item in value) if value else 1  # type: ignore
    else:
        return 0
