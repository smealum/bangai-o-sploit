bangai-o-sploit
===============

contact : sme@lum.sexy

this repo is for bangai-o sploit, a piece of software that lets you execute unsigned code on your nintendo DS by injecting it into Bangai-o Spirits' savegame.
I wrote this a while ago when I wasn't very experienced with this kind of thing, so the code is a complete mess; feel free to improve it and create pull requests on those improvements.

as it stands, running do.bat will extract the executable arm9/arm7 blobs from "input.nds" and inject them into a savegame named "bosnewus.sav". after injecting the save into your cartridge, going into the "Edit mode" menu and pressing the "Custom stage" button will run your code.

this exploit should work fine on any DS, DS lite, DSi, DSi XL, 3DS, 3DS XL or 2DS out there.

please note that this directory contains the Japanese version of bangai-o sploit. use one of the two other directories if your region differs.

dependencies:
ndstool - http://code.google.com/p/psprampatch/downloads/detail?name=NDSTOOL.rar&can=2&q=
armips  - http://www.romhacking.net/utilities/635/
