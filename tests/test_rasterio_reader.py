from rasterio.env import get_gdal_config

from cloudgeometer.readers.rasterio import rasterio_env
from cloudgeometer.s3 import S3Config


def test_rasterio_env_does_not_leave_config_options_behind(monkeypatch):
    monkeypatch.setenv("GDAL_CURL_CA_BUNDLE", "/before.pem")
    with rasterio_env("http://proxy", "/proxy.pem", S3Config()):
        assert get_gdal_config("GDAL_CURL_CA_BUNDLE", normalize=False) == "/proxy.pem"
    # env var changes must still be honored after the env is exited
    monkeypatch.setenv("GDAL_CURL_CA_BUNDLE", "/after.pem")
    assert get_gdal_config("GDAL_CURL_CA_BUNDLE", normalize=False) == "/after.pem"
