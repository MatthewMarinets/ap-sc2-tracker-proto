"""
Update icon_locations.py
Helpful to preserve order from existing icon paths
"""
import json
from .icon_locations import ICON_PATHS
import sys
import os


THIS_DIR = os.path.dirname(__file__)


def main(new_icons_path: str) -> None:
    result: dict[str, list[str]] = {}
    with open(new_icons_path, 'r') as fp:
        new_icons = json.load(fp)
    for key, new_value in new_icons.items():
        if len(new_value) == 1 or len(ICON_PATHS[key]) == 1:
            result[key] = new_value
        elif set(new_value) == set(ICON_PATHS[key]):
            result[key] = ICON_PATHS[key]
        else:
            print(f"warning: {key} changed")
            result[key] = new_value
    result["Kerrigan Level"] = result["1 Kerrigan Level"]
    with open(f'{THIS_DIR}/icon_locations.py', 'w') as fp:
        print('ICON_PATHS = {', file=fp)
        for key, val in result.items():
            print(f' "{key}": [', file=fp)
            for value in val:
                print(f'  "{value}",', file=fp)
            print(f' ],', file=fp)
        print('}', file=fp)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {os.path.basename(__file__)} <icon_sources.json>')
        sys.exit()
    new_icons = sys.argv[1]
    main(new_icons)
