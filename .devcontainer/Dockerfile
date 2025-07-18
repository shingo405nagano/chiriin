FROM mcr.microsoft.com/devcontainers/python:3.12

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get upgrade -y \
    && apt-get -y install --no-install-recommends \
        # GDALに必要なパッケージ
        tzdata \
       gdal-bin \
       libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt