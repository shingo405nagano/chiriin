from typing import Union

import numpy as np
import pandas as pd

UniqueIterable = Union[tuple, list, np.ndarray, pd.Series]


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
