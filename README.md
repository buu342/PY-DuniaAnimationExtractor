# Dunia Engine Animation Extractor

### PLEASE NOTE THIS REPOSITORY IS CURRENTLY WORK IN PROGRESS AND DOES NOT EXTRACT ANIMATIONS YET! YOU CAN FOLLOW ALONG WITH THE DEVELOPMENT OF THIS SCRIPT [HERE](https://knockout.chat/thread/55079)

The aim of this repository is to provide a Python script designed to parse the animation files from [Dunia Engine](https://en.wikipedia.org/wiki/Ubisoft#Dunia_Engine) games (Far Cry, Watch Dogs) into a more useable format. 

The script aims to be completely clean-room, meaning that it is not reliant on leaked code or debug symbols from prototype builds. Reverse engineering solely through the use of a debugger and disassembler.

Currently, only `.mab` files from Far Cry 3 are supported.

Contributions welcome!

### Script Usage:

1. First, unpack the .dat and .fat of your Dunia Engine game of choice. You will need a tool such as [Gibbed 2 Dunia Tools](https://github.com/gibbed/Gibbed.Dunia).
2. Find the model you want to rip the animations from, and grab its `.xbg` file.
3. Find the `.mab` animation you want to convert.
4. Run the script like so:
```
python3 animparser.py animation.mab mesh.xbg
```

### Documentation

The `.mab` format is documented in this project's [GitHub Wiki](../../wiki).

### TODO:

* Successfully retrieve bone rotation data from the animation file
* Successfully retrieve bone translation data from the animation file
* Check if the format supports scale data
* Export all of this data into a usable format, like `.smd`
* Support more games than just Far Cry 3