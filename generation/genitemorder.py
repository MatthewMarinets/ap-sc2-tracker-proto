"""
Helper script to generate a subset of item definitions to copy-paste into itemorder.py
"""
from ..item import item_tables, item_groups, item_parents, item_names
from .. import mission_tables, regions


VALUE_TO_SYMBOL = {item_names.__dict__[x]: x for x in item_names.__dict__ if not x.startswith('_')}


def print_unit_item_groups(unit_list: list[str]) -> None:
    for item_name in unit_list:
        # var_name = item_name.upper().replace("'", '').replace(' ', '_')
        var_name = VALUE_TO_SYMBOL[item_name]
        child_items = [
            symbol_name
            for symbol_name in item_names.__dict__
            if symbol_name.startswith(var_name + '_')]
        child_items = sorted(child_items)
        if child_items:
            print(f'    Upgradeable(item_names.{var_name}, [')
            for child_item in child_items:
                print(f'        item_names.{child_item},')
            print( '    ]),')
        else:
            print(f'        item_names.{var_name},')


def print_terran_items() -> None:
    print_unit_item_groups(item_groups.terran_units + item_groups.terran_buildings)


def print_zerg_items() -> None:
    print_unit_item_groups(item_groups.zerg_units + item_groups.zerg_buildings)


def print_protoss_items() -> None:
    print_unit_item_groups(item_groups.protoss_units + item_groups.protoss_buildings)


def print_faction_globals(race: mission_tables.SC2Race, race_units: set[str]) -> None:
    for item_name, item_data in item_tables.item_table.items():
        if item_data.race != race:
            continue
        if item_name in race_units:
            continue
        if item_data.parent is not None and item_data.parent in race_units:
            continue
        print(f'    item_names.{VALUE_TO_SYMBOL[item_name]},')

# print_terran_items()
# print_zerg_items()
# print_protoss_items()
# print_faction_globals(mission_tables.SC2Race.TERRAN, set(item_groups.terran_units + item_groups.terran_buildings))
# print_faction_globals(mission_tables.SC2Race.ZERG, set(item_groups.zerg_units + item_groups.zerg_buildings + item_groups.zerg_morphs))
print_faction_globals(mission_tables.SC2Race.PROTOSS, set(item_groups.protoss_units + item_groups.protoss_buildings))
