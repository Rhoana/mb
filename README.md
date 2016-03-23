# mbeam

## Requirements
- Requires OpenCV 2.4+
- Python requirements in [requirements.txt](requirements.txt)

## Installation
```bash
$ git clone <mbeam_repo>
$ pip install -e .
```

## Usage

```bash
$ mbeam -p 8080 -a 0.0.0.0
```

## Config
mbeam looks for a yaml file called mbeam.yaml in its current working directory.
The default config for mbeam is:

```yaml
client_tile_size: 512
image_coordinates_file: 'image_coordinates.txt'
metadata_file: 'metadata.txt'
image_prefix: 'thumbnail_'
invert: True
cache_client_tiles: False
client_tile_cache_folder: '/tmp/beam' # on linux - varies by platform
default_data_folder: 'data'
```

All paths are relative to mbeam's current working directory by default. Use
absolute paths to use files and directories in other locations.
