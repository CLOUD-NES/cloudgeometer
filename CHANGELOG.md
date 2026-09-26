# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added PyPI, DOI and license badges to README.md
- Add a logo [#8](https://github.com/CLOUD-NES/cloudgeometer/pull/8)

### Changed

- Pick a free proxy port when none is specified - [#4](https://github.com/CLOUD-NES/cloudgeometer/pull/4)

### Fixed

- rasterio reader now properly sets AWS credentials [#2](https://github.com/CLOUD-NES/cloudgeometer/pull/2)
- rasterio reader no longer leaves GDAL config options behind, which broke SSL verification for later GDAL-based readers [#5](https://github.com/CLOUD-NES/cloudgeometer/pull/5)
- Proxy now fails loudly on busy port [#3](https://github.com/CLOUD-NES/cloudgeometer/pull/3)
- Request logs are no longer dropped (and stopping the proxy no longer hangs) when many requests are logged [#6](https://github.com/CLOUD-NES/cloudgeometer/pull/6)
- Add boto3 dependency to properly setup the rasterio reader with AWS credentials. [#7](https://github.com/CLOUD-NES/cloudgeometer/pull/7)

## [0.1.0] - 2026-09-16

First package release!
