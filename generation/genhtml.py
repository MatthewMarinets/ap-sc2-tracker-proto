from typing import Any, Iterable
from .itemorder import *
from .icon_locations import ICON_PATHS
from ..item import item_tables, item_groups
from ..item.item_descriptions import item_descriptions
import os
import sys


def iconpath(itemname: str, index: int) -> str:
    iconlist = ICON_PATHS.get(itemname)
    if iconlist is None:
        print(f'=== No icons: {itemname}')
        result = ICON_PATHS['Nothing'][0]
    elif len(iconlist) <= index:
        print(f'=== OOB: {itemname} @ index {index}')
        result = ICON_PATHS['Nothing'][0]
    else:
        result = iconlist[index]
    return 'https://matthewmarinets.github.io/ap_sc2_icons/' + result


def title_suffix(item_name: str) -> str:
    result = item_descriptions.get(item_name)
    if result is None:
        return ''
    return f'&#10;{result.replace("\n", "&#10;")}'


def _sanitize_css_filename(filename: str) -> str:
    return filename.replace("'", "").replace(".", "-").replace("@", "")


HIDDEN_CLASSES = set(item_groups.unreleased_items)
HIDDEN_ITEMS = set(item_groups.legacy_items)


def fetch_atlas_data(atlas_version: str) -> tuple[int, dict[str, int]]:
    metadata_url = f"https://matthewmarinets.github.io/ap_sc2_icons/data/atlas.{atlas_version}.json"
    print(f"Requesting from {metadata_url}")
    import requests
    import json
    result = requests.get(metadata_url, headers={'accept': 'application/json'})
    content = result.content.decode(result.apparent_encoding)
    atlas_data = json.loads(content)
    return atlas_data["num_images"], atlas_data["order"]


def main(arguments: list[str]) -> None:
    if '-h' in arguments or '--help' in arguments or 'help' in arguments:
        print(f"Usage: python -m {sys.modules[__name__]} [-jinja] [-atlas=<version>]")
        print(f"  -jinja -- output in jinja template format")
        print( '  -atlas="<version>" -- fetch atlas data for version <version> (format like v4.0.0)')
        print( "    from https://matthewmarinets.github.io/ap_sc2_icons and use the atlas path for images")
        print( "    (will also generate a sc2TrackerAtlas.css file)")

    if '-jinja' in arguments:
        OUTPUT_FOR_JINJA = True
    else:
        OUTPUT_FOR_JINJA = False
    
    atlas_version = ''
    for argument in arguments:
        if argument.startswith("-atlas="):
            atlas_version = argument.split("=", 1)[1]
    if atlas_version:
        atlas_url = f"https://matthewmarinets.github.io/ap_sc2_icons/icons/atlas.{atlas_version}.png"
        atlas_count, atlas_order = fetch_atlas_data(atlas_version)
        def img_src(itemname: str, index: int) -> str:
            return atlas_url
        def img_class(itemname: str, index: int) -> str:
            key = os.path.basename(iconpath(itemname, index))
            return f' {_sanitize_css_filename(key)}'
        with open("WebHostLib/static/styles/sc2TrackerAtlas.css", 'w') as fp2:
            for key, order in atlas_order.items():
                translate_percent = 50 - 100*(order+0.5)/atlas_count
                print(f'.{_sanitize_css_filename(key)}{{', file=fp2)
                print(f"  clip-path: xywh(0 {100*order/atlas_count}% 100% {100/atlas_count}%);", file=fp2)
                print(f"  transform: scale(1, {atlas_count}) translate(0, {translate_percent}%);", file=fp2)
                print("}\n", file=fp2)
    else:
        img_src = iconpath
        def img_class(itemname: str, index: int) -> str:
            return ""

    fp = open('zout.html', 'w')
    def emit(string: str, **kwargs) -> None:
        print(string, **kwargs, file=fp)


    class EmitItemIcon:
        def __init__(self) -> None:
            self.subsection = ''
            self.subsection_index = 0

        def emit_item_icon(self, item: str | Upgradeable | FillerCounter | SectionBreak | SubSection, indent: int = 4) -> None:
            i = '  ' * indent
            if isinstance(item, str):
                item_data = item_tables.item_table[item]
                if item_data.quantity == 1:
                    # Normal items
                    suffix = ''
                    class_suffix = img_class(item, 0)
                    if item in HIDDEN_ITEMS:
                        class_suffix += ' hidden-item'
                        suffix = f' class="{class_suffix[1:]}"'
                    if OUTPUT_FOR_JINJA:
                        emit(f'{i}<div class="f {{{{\'unacquired\' if inventory[{item_data.code}] == 0}}}}"><img src="{img_src(item, 0)}" title="{item}{title_suffix(item)}" class="{class_suffix}"></div>')
                    else:
                        emit(f'{i}<img id="{item}" src="{img_src(item, 0)}" title="{item}{title_suffix(item)}"{suffix}>')
                else:
                    # Progressive items
                    if OUTPUT_FOR_JINJA:
                        emit(f'{i}<div class="progressive lvl-{{{{[inventory[{item_data.code}], {item_data.quantity}]|min}}}}">')
                    else:
                        emit(f'{i}<div id="{item}" class="progressive lvl-0" data-max-level="{item_data.quantity}">')
                    for level in range(0, item_data.quantity):
                        emit(f'{i}  <div class="f"><img src="{img_src(item, level)}" title="{item} - Level {level+1}{title_suffix(item)}" class="{img_class(item, level)}"></div>')
                    emit(f'{i}</div>')
            elif isinstance(item, Spacer):
                emit(f'{i}<div class="spacer"></div>')
            elif isinstance(item, Upgradeable):
                # Item blocks
                second_class = ''
                if item.parent_items and item.parent_items[0] in HIDDEN_CLASSES:
                    second_class = ' hidden-class'
                emit(f'{i}<div id="class-{item.classname}" class="item-class{self.subsection}{second_class}">')
                if item.parent_items:
                    emit(f'{i}  <div class="item-class-header">')
                    for parent_item in item.parent_items:
                        self.emit_item_icon(parent_item, indent=indent+2)
                    emit(f'{i}  </div>')
                if item.child_items:
                    emit(f'{i}  <div class="item-class-upgrades">')
                    for child in item.child_items:
                        self.emit_item_icon(child, indent=indent+2)
                    emit(f'{i}  </div>')
                emit(f'{i}</div>')
            elif isinstance(item, FillerCounter):
                # Filler items
                emit(f'{i}<div class="item-counter">')
                emit(f'{i}  <div class="f"><img src="{img_src(item.item_name, 0)}" title="{item.item_name}{title_suffix(item.item_name)}" class="{img_class(item.item_name, 0)}"></div>')
                emit(f'{i}  <span class="item-count">{{{{{item.var_name}}}}}</span>')
                emit(f'{i}</div>')
            elif isinstance(item, SectionBreak):
                small_i = '  '*(indent-1)
                emit(f'{small_i}</div>')
                emit(f'{small_i}<div class="section-body">')
                self.subsection = ''
            elif isinstance(item, SubSection):
                self.subsection_index += 1
                emit(f'{i}<div class="ss-header">')
                # emit(f'{i}  <input type="checkbox" class="ss-{self.subsection_index}-toggle">')
                emit(f'{i}  &#x2014; {item.name} &#x2014;')
                emit(f'{i}</div>')
                self.subsection = f' ss-{self.subsection_index}'
                
                # Force linebreaks:
                # self.subsection_index += 1
                # small_i = '  '*(indent-1)
                # emit(f'{small_i}</div>')
                # emit(f'{small_i}<div class="ss-header">')
                # emit(f'{small_i}  <input type="checkbox" class="ss-{self.subsection_index}-toggle">')
                # emit(f'{small_i}  &#x2014; {item.name} &#x2014;')
                # emit(f'{small_i}</div>')
                # emit(f'{small_i}<div class="section-body">')
                # self.subsection = f' ss-{self.subsection_index}'
            else:
                assert False, f"Unknown type {type(item)}"


    def emit_section_start(section_id: str, subsections: Iterable[str] = (), start_minimized: str = '') -> None:
        if start_minimized and OUTPUT_FOR_JINJA:
            checked = f'{{{{ \'checked="t"\' if not {start_minimized}}}}}'
        elif start_minimized:
            checked = ' checked="t"'
        else:
            checked = ''
        emit(f'    <div id="{section_id}" class="tracker-section">')
        emit(f'      <div class="section-title">')
        emit(f'        <input type="checkbox" class="collapse-section"{checked}>')
        emit(f'        <h2>{section_id.replace("-", " ").title()}</h2>')
        emit(f'      </div>')
        if subsections:
            emit(f'      <div class="section-body-2">')
            emit(f'        <div class="section-toc">')
            for index, subsection in enumerate(subsections, start=1):
                emit(f'          <div class="toc-box">')
                emit(f'            <input type="checkbox" class="ss-{index}-toggle">')
                emit(f'            {subsection}')
                emit(f'          </div>')
            emit(f'        </div>')
        emit(f'      <div id="section-{section_id.split("-", 1)[0]}" class="section-body">')

    def emit_section_end(subsections: Iterable = ()) -> None:
        if subsections:
            emit('      </div>')
        emit('      </div>')
        emit('    </div>')


    def get_subsections(contents: list) -> list[str]:
        result = []
        for item in contents:
            if isinstance(item, SubSection):
                result.append(item.name)
            elif isinstance(item, SectionBreak):
                break
        return result


    def emit_section(section_id: str, contents: list, start_minimized: bool = False) -> None:
        subsections = get_subsections(contents)
        emit_section_start(section_id, subsections, start_minimized)
        e = EmitItemIcon()
        for item in contents:
            e.emit_item_icon(item)
        emit_section_end(subsections)


    def emit_locations_section() -> None:
        emit_section_start("locations")
        emit_section_end()


    def emit_keys_section() -> None:
        emit_section_start("keys", start_minimized=True)
        emit('        <ol id="keylist">')
        for x in ('Key 1', 'Key 2', 'Raynor Key', 'Artanis Key', 'Vorazun Key'):
            emit(f'          <li id="{x}" data-count="1">{x}</li>')
        emit('        </ol>')
        emit_section_end()


    emit_section('filler-items', FILLER_ITEMS)
    emit_section('terran-items', TERRAN_ITEMS)
    emit_section('zerg-items', ZERG_ITEMS)
    emit_section('protoss-items', PROTOSS_ITEMS)
    emit_section('nova-items', NOVA_ITEMS, 'nova_present')
    emit_section('kerrigan-items', KERRIGAN_ITEMS, 'kerrigan_present')
    # emit_keys_section()
    # emit_locations_section()

    fp.close()


main(sys.argv)
