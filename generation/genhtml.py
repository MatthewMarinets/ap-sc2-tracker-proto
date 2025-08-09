from typing import Any, Iterable
from .itemorder import *
from .icon_locations import ICON_PATHS
from ..item import item_tables, item_groups
from ..item.item_descriptions import item_descriptions


OUTPUT_FOR_JINJA = True


fp = open('zout.html', 'w')
def emit(string: str, **kwargs) -> None:
    print(string, **kwargs, file=fp)


def iconpath(itemname: str, index: int) -> Any:
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


HIDDEN_CLASSES = set(item_groups.unreleased_items)
HIDDEN_ITEMS = set(item_groups.legacy_items)


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
                class_suffix = ''
                if item in HIDDEN_ITEMS:
                    class_suffix = ' hidden-item'
                    suffix = f' class="{class_suffix[1:]}"'
                if OUTPUT_FOR_JINJA:
                    emit(f'{i}<img id="{item}" src="{iconpath(item, 0)}" title="{item}{title_suffix(item)}" class="{{{{\'acquired\' if inventory[{item_data.code}] > 0}}}}{class_suffix}">')
                else:
                    emit(f'{i}<img id="{item}" src="{iconpath(item, 0)}" title="{item}{title_suffix(item)}"{suffix}>')
            else:
                # Progressive items
                if OUTPUT_FOR_JINJA:
                    emit(f'{i}<div id="{item}" class="progressive lvl-{{{{[inventory[{item_data.code}], {item_data.quantity}]|min}}}}">')
                else:
                    emit(f'{i}<div id="{item}" class="progressive lvl-0" data-max-level="{item_data.quantity}">')
                for level in range(0, item_data.quantity):
                    emit(f'{i}  <img src="{iconpath(item, level)}" title="{item} - Level {level+1}{title_suffix(item)}">')
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
            emit(f'{i}  <img src="{iconpath(item.item_name, 0)}" title="{item.item_name}{title_suffix(item.item_name)}">')
            emit(f'{i}  <span class="item-count">{{{{kerrigan_level}}}}</span>')
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
