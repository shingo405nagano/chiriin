# Python - DevContiner公式イメージ
# * GitHub | devcontainer/pyhton : https://github.com/devcontainers/images/tree/main/src/python
FROM mcr.microsoft.com/devcontainers/python:3.12

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip\
    && pip install wheel\
    && pip install setuptools\
    && pip install requests\
    && pip install numpy\
    && pip install matplotlib\
    && pip install japanize-matplotlib\
    && pip install pandas\
    && pip install shapely\
    && pip install pyproj\
    && pip install geopandas\
    && pip install pydantic\
    && pip install aiohttp\
    && pip install pymupdf\
    && pip install ruff\
    && pip install pytest\
    && pip install pytest-cov\
    && pip install pytest-xdist\
    && pip install pytest-html