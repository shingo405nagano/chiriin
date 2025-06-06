import time

import numpy as np
import requests


def download_tile_array(url: str) -> np.ndarray:
    """
    ## Summary:
        地理院の標高APIを利用して、指定されたURLからタイルデータを取得する関数です。
        タイルデータは`bytes`型で返されるので、Float型の`np.ndarray`に変換して返しマス。
    """
    max_retries = 5
    retries = 0
    while True:
        if max_retries < retries:
            raise Exception(
                "Max retries exceeded, unable to download tile data. "
                f"\nRequest URL: {url}"
            )
        try:
            response = requests.get(url)
            if response.status_code != 200:
                retries += 1
                time.sleep(0.5)
                continue
            response_content = response.content
            # np.ndarrayに変換する処理を追加
            # ここでは、タイルデータがテキスト形式であることを前提としています。
            # もしバイナリ形式であれば、適切な変換方法を使用してください。
            tile_txt = response_content.decode("utf-8")
            # 'e'を'-9999'に置き換え、NaNに変換するための処理
            tile_data = tile_txt.replace("e", "-9999").splitlines()
            tile_data = [[float(v) for v in line.split(",")] for line in tile_data]
        except Exception as e:
            print(f"Error downloading tile: {e}")
            time.sleep(1)
        else:
            break
    ary = np.array(tile_data, dtype=np.float32)
    ary[ary == -9999] = np.nan  # -9999をNaNに変換
    return ary
