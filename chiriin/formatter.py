import datetime
from decimal import Decimal
from typing import Any, Iterable

from chiriin.utils import dimensional_count


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
            try:
                return datetime.datetime.strptime(dt, fmt).replace(microsecond=0)
            except ValueError:
                continue
        try:
            return datetime.datetime.fromisoformat(dt).replace(tzinfo=None, microsecond=0)
        except ValueError:
            raise ValueError(f"Unsupported datetime format: {dt}")  # noqa: B904

    raise TypeError(f"Expected datetime or str, got {type(dt)}")


def _intermediate(arg_index, kward, *args, **kwargs) -> dict[str, Any]:
    """
    ## Description:
        Helper function to determine if the argument is in args or kwargs.
    ## Args:
        arg_index (int):
            The index of the argument to check.
        kward (str):
            The keyword argument to check.
        *args:
            Variable length argument list.
        **kwargs:
            Arbitrary keyword arguments.
    ## Returns:
        dict:
            A dictionary containing whether the argument is in args or kwargs and its value.
    """
    in_args = True
    value = None
    if arg_index < len(args):
        value = args[arg_index]
    else:
        in_args = False
        value = kwargs[kward]
    return {"in_args": in_args, "value": value}


def _return_value(value: Any, data: dict[str, Any], args, kwargs) -> Any:
    """
    ## Description:
        Helper function to return the modified args and kwargs after type checking.
    ## Args:
        value (Any):
            The value to be set in args or kwargs.
        data (dict[str, Any]):
            The data containing information about the argument index and keyword.
        *args:
            Variable length argument list.
        **kwargs:
            Arbitrary keyword arguments.
    ## Returns:
        dict:
            A dictionary containing the modified args and kwargs.
    """
    if data["in_args"]:
        args = list(args)
        args[data["arg_index"]] = value
    else:
        kwargs[data["kward"]] = value
    return {"args": args, "kwargs": kwargs}


def type_checker_float(arg_index: int, kward: str) -> float:
    """
    ## Description:
        Decorator to check if a function argument is a float or convertible to float.
    ## Args:
        arg_index (int):
            The index of the argument to check if it is a float.
        kward (str):
            The keyword argument to check if it is a float.
    ## Returns:
        float:
            The float value of the argument.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            data = _intermediate(arg_index, kward, *args, **kwargs)
            data["arg_index"] = arg_index
            data["kward"] = kward
            value = data["value"]
            try:
                value = float(value)
            except Exception:
                raise TypeError(f"Argument '{kward}' must be a float or convertible to float, got {type(value)}")  # noqa: B904
            else:
                result = _return_value(value, data, args, kwargs)
                return func(*result["args"], **result["kwargs"])

        return wrapper

    return decorator


def type_checker_integer(arg_index: int, kward: str) -> int:
    """
    ## Description:
        Decorator to check if a function argument is an integer or convertible to integer.
    ## Args:
        arg_index (int):
            The index of the argument to check if it is an integer.
        kward (str):
            The keyword argument to check if it is an integer.
    ## Returns:
        int:
            The integer value of the argument.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            data = _intermediate(arg_index, kward, *args, **kwargs)
            data["arg_index"] = arg_index
            data["kward"] = kward
            value = data["value"]
            try:
                value = int(value)
            except Exception:
                raise TypeError(f"Argument '{kward}' must be an integer or convertible to integer, got {type(value)}")  # noqa: B904
            else:
                result = _return_value(value, data, args, kwargs)
                return func(*result["args"], **result["kwargs"])

        return wrapper

    return decorator


def type_checker_datetime(arg_index: int, kward: str) -> datetime.datetime:
    """
    ## Description:
        Decorator to check if a function argument is a datetime object or a string that can be converted to datetime.
    ## Args:
        arg_index (int):
            The index of the argument to check if it is a datetime.
        kward (str):
            The keyword argument to check if it is a datetime.
    ## Returns:
        datetime.datetime:
            The datetime object with microseconds set to 0.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            data = _intermediate(arg_index, kward, *args, **kwargs)
            data["arg_index"] = arg_index
            data["kward"] = kward
            value = data["value"]
            value = datetime_formatter(value)
            result = _return_value(value, data, args, kwargs)
            return func(*result["args"], **result["kwargs"])

        return wrapper

    return decorator


def type_checker_decimal(arg_index: int, kward: str) -> float:
    """
    ## Description:
        Decorator to check if a function argument is a decimal or convertible to decimal.
    ## Args:
        arg_index (int):
            The index of the argument to check if it is a decimal.
        kward (str):
            The keyword argument to check if it is a decimal.
    ## Returns:
        float:
            The decimal value of the argument.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            data = _intermediate(arg_index, kward, *args, **kwargs)
            data["arg_index"] = arg_index
            data["kward"] = kward
            value = data["value"]
            if isinstance(value, Decimal):
                return func(*args, **kwargs)
            try:
                value = Decimal(f"{float(value)}")
            except Exception:
                raise TypeError(f"Argument '{kward}' must be a decimal or convertible to decimal, got {type(value)}")  # noqa: B904
            else:
                result = _return_value(value, data, args, kwargs)
                return func(*result["args"], **result["kwargs"])

        return wrapper

    return decorator


@type_checker_float(arg_index=0, kward="value")
def float_formatter(value: int | float | str) -> float:
    """
    ## Description:
        Function to format a float value.
    ## Args:
        value (int | float | str):
            The value to be formatted as a float.
            It can be an integer, a float, or a string that can be converted to a float.
    ## Returns:
        float:
            The formatted float value.
    """
    return value


@type_checker_integer(arg_index=0, kward="value")
def integer_formatter(value: int | float | str) -> int:
    """
    ## Description:
        Function to format an integer value.
    ## Args:
        value (int | float | str):
            The value to be formatted as an integer.
            It can be an integer, a float, or a string that can be converted to an integer.
    ## Returns:
        int:
            The formatted integer value.
    """
    return value


def iterable_float_formatter(values: Iterable) -> list[float]:
    """
    ## Description:
        Function to format one-dimensional iterable values as a list of floating-point numbers.
    ## Args:
        values (Iterable):
            An iterable containing values that can be converted to float.
            It can be a list, tuple, or any other iterable containing numeric values.
            However, it must be one-dimensional iterable.
    ## Returns:
        list[float]:
            A list of formatted float values.
    """
    count = dimensional_count(values)
    assert count == 1, f"Expected one-dimensional iterable, got {count}D iterable."
    return [float_formatter(value) for value in values]


def iterable_integer_formatter(values: Iterable) -> list[int]:
    """
    ## Description:
        Function to format one-dimensional iterable values as a list of integers.
    ## Args:
        values (Iterable):
            An iterable containing values that can be converted to integer.
            It can be a list, tuple, or any other iterable containing numeric values.
            However, it must be one-dimensional iterable.
    ## Returns:
        list[int]:
            A list of formatted integer values.
    """
    count = dimensional_count(values)
    assert count == 1, f"Expected one-dimensional iterable, got {count}D iterable."
    return [integer_formatter(value) for value in values]


def iterable_decimalize_formatter(values: Iterable) -> list[Decimal]:
    """
    ## Description:
        Function to format one-dimensional iterable values as a list of Decimal numbers.
    ## Args:
        values (Iterable):
            An iterable containing values that can be converted to Decimal.
            It can be a list, tuple, or any other iterable containing numeric values.
            However, it must be one-dimensional iterable.
    ## Returns:
        list[Decimal]:
            A list of formatted Decimal values.
    """
    count = dimensional_count(values)
    assert count == 1, f"Expected one-dimensional iterable, got {count}D iterable."
    return [Decimal(f"{float(value)}") for value in values]
