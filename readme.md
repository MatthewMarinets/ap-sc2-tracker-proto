# AP sc2 tracker prototype
Prototype for creating the webtracker for Archipelago Starcraft 2.

Python scripts are used to generate a template of the HTML used by the tracker.
The scripts may be adjusted to generate a jinja template instead so that it can by
hydrated by the webclient at the time that the user fetches the tracker.

To use the generation scripts, create a symlink from the Archipelago repository at
`worlds/sc2/tracker`, pointing to this repository's `generation/` directory.

On Windows:
```bat
cd <path to Archipelago repo>
mklink /D worlds\sc2\tracker <path to tracker repo>\generation
python -m worlds.sc2.tracker.genhtml
```

On Linux:
```bash
cd <path to Archipelago repo>
ln -s <path to tracker repo>\generation worlds/sc2/tracker
python3 -m worlds.sc2.tracker.genhtml
```

This will generate the HTML at `zout.html`.

## Script overview
* genhtml.py is the actual HTML generation script
* icon_locations.py is a big map of item name to icon location. It is copy-pasted from the sc2 icon repo
  * Some manual adjustments had to be made to correct the order of progressive items with multiple icons
* itemorder.py defines the order that the items appear in the HTML output
* doublecheck.py and genitemorder.py are helper scripts to generate or validate icons in itemorder.py
