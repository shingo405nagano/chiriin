import time

import numpy as np
import requests


def download_tile_array(url: str) -> np.ndarray:
    """
    ## Summary:
        地理院の標高APIを利用して、指定されたURLからタイルデータを取得する関数です。
        タイルデータは`bytes`型で返されるので、Float型の`np.ndarray`に変換して返しマス。
    """
    while True:
        try:
            response = requests.get(url)
            response_content = response.content
            # np.ndarrayに変換する処理を追加
            # ここでは、タイルデータがテキスト形式であることを前提としています。
            # もしバイナリ形式であれば、適切な変換方法を使用してください。
            tile_txt = response_content.decode("utf-8")
            tile_data = tile_txt.replace("e", "-9999").splitlines()
            tile_data = [[float(v) for v in line.split(",")] for line in tile_data]
        except Exception as e:
            print(f"Error downloading tile: {e}")
            time.sleep(1)
        else:
            break
    return np.array(tile_data, dtype=np.float32)
