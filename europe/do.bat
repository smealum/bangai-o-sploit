@echo off
ndstool -x input.nds -7 arm7.bin -9 arm9.bin
cp bosnewus_proto.SAV bosnewus.SAV
armips.exe test.s
py -3 bosfix.py
cp bosnewus.SAV bangai_europe.SAV
pause
