# doom-cmd

**This project is a WORK IN PROGRESS! Make sure to read the sections below before using.**

doom-cmd is a command-line frontend/wrapper for launching Doom. It works similarly to launching the game manually from the command-line, but provides some advantages:

- Launch all your favorite source ports from a single app, with a configurable list.

- Set one or more directories as an IWADs or PWADs directory, and easily choose IWADs or PWADs just by typing their name, instead of a full path.

- Set a default source port and/or IWAD, for when either isn't specified.

- Remembers the last source port and IWAD you selected, and can be configured to launch them by default.

- Short parameters for common things like setting the skill level, complevel, or warping to a map.

## Requirements

doom-cmd is distributed in two formats:

- **(NOT YET AVAILABLE)** Binaries bundling all the dependencies. These can be run as-is without installing anything else.

- Python script. This requires [Python](https://www.python.org/) to be installed in your system. Version 3.11.1 has been tested, **there is no guarantee that other versions (especially older ones) will work.**

## Configuration

Start doom-cmd for the first time. The `config.ini` and `engines.ini` files should be created in the app directory.

```
doom-cmd
```

Open `engines.ini` and add source ports to your liking. Any `Path` can be used, below is just an example.

```
[gzdoom]
Path = C:\path\to\gzdoom\gzdoom.exe

[nugget-doom]
Path = C:\path\to\nugget-doom\nugget-doom.exe
```

Open `config.ini` and edit it if necessary.

| Key | Explanation | Default |
| --- | ----------- | ------- |
| `iwadpath` | Path to one or more directories with IWADs. On Windows, use a semicolon ( ; ) separator between path names. On Unix-like systems (e.g. macOS, Linux), use a colon ( : ). | doom-cmd directory |
| `pwadpath` | Same as above, but for PWADs. | doom-cmd directory |
| `defaultengine` | Source port to use if none specified when running doom-cmd. Use the name of a source port defined in `engines.ini`. | -1 (most recently used) |
| `mostrecentengine` | Most recently used source port. No need to change this manually. | -1 (none used yet) |
| `defaultiwad` | IWAD to use if none specified when running doom-cmd. Use the name of an IWAD present in one of the paths defined in `iwadpath`. | -1 (most recently used) |
| `mostrecentiwad` | Most recently used IWAD. No need to change this manually. | -1 (none used yet) |

## Usage

Below are some examples of using this app.

Run the default source port with the default IWAD and no PWADs:

```
doom-cmd
```

Play Ultimate Doom with Voxel Doom mod:

```
doom-cmd --engine gzdoom --iwad doomu --pwad cheello_voxels_v2_1
```

Play Eviternity using the Nugget Doom source port, warping to MAP16 on UV and complevel 11, fast monsters:

```
doom-cmd --engine nugget-doom --iwad doom2 --pwad eviternity -s4 -w16 --cl 11 -fast
```

Example of PWAD in a subdirectory, and multiple PWADs:

```
doom-cmd --pwad sigil/sigil_v1_21 cheello_voxels_v2_1
```

Load an IWAD in a path different from those specified in `iwadpath`:

```
doom-cmd --iwadfp C:\path\to\another-iwad.wad
```

Show an help message:

```
doom-cmd -h
```

## Building

Binaries are built using PyInstaller, which bundles a Python application and all its dependencies into a single package. Follow the instructions at [PyInstaller's manual](https://pyinstaller.org/en/stable/). The Quickstart section should be enough to create a binary for doom-cmd.
