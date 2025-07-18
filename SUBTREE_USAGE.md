# Subtreeとしての利用方法

このプロジェクトを他のプロジェクトのSubtreeとして利用する場合のインポート方法について説明します。

## 方法1: ルートレベルでのインポート（推奨）

プロジェクトのルート `__init__.py` で主要なクラスと関数を再エクスポートしているため、以下のようにインポートできます：

```python
# Subtreeとして追加した場合でも、パスを変更する必要がありません
from chiriin import MAG_DATA, type_checker_float, dms_to_degree, MeshCode

# または、必要に応じて個別にインポート
from chiriin import XY, XYZ, MapEditor, SemiDynamic
```

## 方法2: モジュール別インポート

特定のモジュールから直接インポートしたい場合：

```python
# 通常の利用
from chiriin.config import MAG_DATA
from chiriin.formatter import type_checker_float
from chiriin.geometries import dms_to_degree
from chiriin.mesh import MeshCode

# Subtreeとして利用する場合（パスを調整）
from your_project.chiriin.config import MAG_DATA
from your_project.chiriin.formatter import type_checker_float
from your_project.chiriin.geometries import dms_to_degree
from your_project.chiriin.mesh import MeshCode
```

## 方法3: 相対インポート用のエイリアス設定

プロジェクト内で相対インポート用のエイリアスを設定する方法：

```python
# your_project/utils/chiriin_imports.py
try:
    # 通常の利用時
    from chiriin.config import MAG_DATA
    from chiriin.formatter import type_checker_float
    from chiriin.geometries import dms_to_degree
    from chiriin.mesh import MeshCode
except ImportError:
    # Subtreeとして利用時
    from your_project.chiriin.config import MAG_DATA
    from your_project.chiriin.formatter import type_checker_float
    from your_project.chiriin.geometries import dms_to_degree
    from your_project.chiriin.mesh import MeshCode

# その他のファイルでは
from your_project.utils.chiriin_imports import MAG_DATA, type_checker_float, dms_to_degree, MeshCode
```

## 推奨される使用方法

最も柔軟で保守しやすいのは**方法1**です。これにより：

1. インポートパスを変更する必要がない
2. Subtreeとして利用する際の設定が最小限
3. コードの可読性が向上
4. 将来的な変更に対する耐性が高い

## パッケージとしてのインストール

Subtreeではなく、パッケージとしてインストールして利用することも可能です：

```bash
pip install -e /path/to/chiriin
```

この場合、インポートパスは常に一定になります：

```python
from chiriin import MAG_DATA, type_checker_float, dms_to_degree, MeshCode
```
