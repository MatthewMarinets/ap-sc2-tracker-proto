"""
Parse itemorder.py to check for coverage over all symbols in item_names.py
"""
import os
import re
from ..item import item_names
THIS_DIR = os.path.dirname(__file__)

with open(f'{THIS_DIR}/itemorder.py', 'r') as fp:
    contents = fp.read()

item_name_pattern = re.compile(r'item_names\.(\w+)')
found_item_names = item_name_pattern.findall(contents)

# print(found_item_names)
existing_item_names = set(x for x in item_names.__dict__ if not x.startswith('_'))

s = set()
for item_name in found_item_names:
    if item_name in s:
        print(f'{item_name} was duplicated')
    s.add(item_name)

print(existing_item_names - s)
