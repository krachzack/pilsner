# pilsner
This is a work in progress to create a binding to the pils library for blender.

## Install
Put pilsner.py to your startup scripts. If you use blender on a mac, the correct
path is `/Applications/blender.app/Contents/Resources/2.78/scripts/startup`. The
version number may of course be different on your installation.

## How to use it
Currently, pilsner does not use the [pils](https://github.com/krachzack/pils)
library directly but instead requires the command line tool [lager](https://github.com/krachzack/lager) to write a JSON file to `~/out.json`.

You start lager like this:

    lager config/your-config.yaml ~/out.json

Then, you can start pilsner by starting the operator `Load Pils JSON into current
 scene`. You can do this by hitting the space bar in the 3D view , typing some
filter text and clicking on the item.

Now, blender is in pils mode. The current scene contents are deleted and replaced
with the placement rules in out.json. Should the JSON file change in pils mode,
the scene is again reloaded. Note that blender will become unresponsive while
in pils mode. Hit the escape key to exit pils mode.
