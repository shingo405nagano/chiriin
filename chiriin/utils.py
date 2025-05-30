import datetime


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
            return datetime.datetime.fromisoformat(dt).replace(
                tzinfo=None, microsecond=0
            )
        except Exception:
            raise ValueError(f"Unsupported datetime format: {dt}")
    raise TypeError(f"Expected datetime or str, got {type(dt)}")