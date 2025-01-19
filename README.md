![Intellireading.com](https://raw.githubusercontent.com/0x6f677548/intellireading-www/main/src/img/intellireading.png)
# Standalone tool and library

[![PyPI - Version](https://img.shields.io/pypi/v/intellireading-cli.svg)](https://pypi.org/project/intellireading-cli)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/intellireading-cli.svg)](https://pypi.org/project/intellireading-cli)
[![Deploy to ghcr.io](https://github.com/0x6f677548/intellireading-backend/actions/workflows/build-and-publish-to-ghcr.yml/badge.svg)](https://github.com/0x6f677548/intellireading-backend/actions/workflows/build-and-publish-to-ghcr.yml)
[![Lint](https://github.com/0x6f677548/intellireading-cli/actions/workflows/lint.yml/badge.svg)](https://github.com/0x6f677548/intellireading-cli/actions/workflows/lint.yml)
[![Test](https://github.com/0x6f677548/intellireading-cli/actions/workflows/test.yml/badge.svg)](https://github.com/0x6f677548/intellireading-cli/actions/workflows/test.yml)


Intellireading is a CLI tool with commands to accelerate your reading experience. It can also be used as a python library.
Currently, it supports metaguiding an EPUB, KEPUB, XHTML, or HTML file (more features coming):
```console
> intellireading metaguide-epub --input_file mybook.epub --output_file mybook_metaguided.epub
```
Example of a text converted to a metaguided text:
![Intellireading.com](https://raw.githubusercontent.com/0x6f677548/intellireading-www/main/src/img/sample.png) 


This repo is part of the [Intellireading](https://intellireading.com/) project, which aims to help people with dyslexia, ADHD, or anyone who wants to improve their reading focus and speed. 

## [Other Intellireading Code Repositories](https://github.com/stars/0x6f677548/lists/intellireading)
- [Intellireading website](https://www.github.com/0x6f677548/intellireading-www), which allows anyone to convert an Epub to the metaguided version.
- [Backend Servers](https://www.github.com/0x6f677548/intellireading-backend), that support the Intellireading website.
- [CLI Tool](https://www.github.com/0x6f677548/intellireading-cli). A standalone tool and library that can be used to metaguide epub files.
- [Calibre Plugins](https://www.github.com/0x6f677548/intellireading-calibre-plugins). A set of plugins that can be used to metaguide epub files using Calibre.


## What is Epub Metaguiding?
**Metagu**iding **i**s **a** **techn**ique **th**at **ca**n **b**e **us**ed **t**o **impr**ove **yo**ur **read**ing **foc**us **an**d **spe**ed **(some**times **cal**led **Bio**nic **Readi**ng). **I**t **i**s **bas**ed **o**n **th**e **id**ea **th**at **yo**u **ca**n **us**e **a** **vis**ual **gui**de **t**o **he**lp **yo**ur **ey**es **foc**us **o**n **th**e **te**xt **yo**u **ar**e **read**ing. **I**n **th**is **cas**e, **th**e **vis**ual **gui**de **i**s **do**ne **b**y **bold**ing **a** **pa**rt **o**f **th**e **tex**t, **crea**ting **vis**ual **anch**ors **th**at **yo**ur **ey**es **ca**n **us**e **t**o **foc**us **o**n **th**e **tex**t. **Th**is **i**s **simi**lar **t**o **th**e **wa**y **a** **fin**ger **ca**n **b**e **us**ed **t**o **gui**de **yo**ur **ey**es **alo**ng **a** **li**ne **o**f **tex**t, **whi**ch **ha**s **be**en **sho**wn **t**o **impr**ove **read**ing **spe**ed **an**d **foc**us. ([**stu**dy: **"Do**es **finger-t**racking **poi**nt **t**o **chi**ld **read**ing **strate**gies"](https://ceur-ws.org/Vol-2769/paper_60.pdf))

**Howe**ver, **unl**ike **a** **fing**er, **th**e **vis**ual **gui**de **i**s **no**t **distra**cting, **an**d **i**t **ca**n **b**e **us**ed **t**o **gui**de **yo**ur **ey**es **alo**ng **mult**iple **lin**es **o**f **te**xt **a**t **onc**e. **Th**is **all**ows **yo**u **t**o **re**ad **fast**er, **an**d **wi**th **le**ss **effo**rt.

**Metagu**iding **i**s **partic**ulary **use**ful **fo**r **peo**ple **wi**th **dysl**exia **o**r **ADH**D, **bu**t **i**t **ca**n **b**e **us**ed **b**y **any**one **wh**o **wan**ts **t**o **impr**ove **the**ir **read**ing **foc**us **an**d **spe**ed. **Fo**r **mo**re **inform**ation, **vis**it **th**e [**Intelli**reading **webs**ite.](https://intellireading.com/)

## Features

Intellireading commands can be used to:
- **Metaguide an EPUB file**: Metaguide an EPUB file, transforming it into a metaguided EPUB file, by transforming all XHTML files in the EPUB file into metaguided XHTML files.
- **Metaguide an XHTML file**: Metaguide an XHTML file, transforming it into a metaguided XHTML file.
- **Metaguide a directory**: Metaguide all files in a directory, transforming all EPUB, XHTML, and HTML files into metaguided files.


## Installation
Intellireading is a command line tool that can be used in Windows, Linux, and MacOS. It is written in Python and can be used as a module or as a standalone tool, as long as you have Python >3.7 installed (or Docker).

### pip
To install it, you can use pip:
```console
> pip install intellireading-cli
> intellireading --help
```

### From source code
You can also install it from the source code:
```console
> git clone https://github.com/0x6f677548/intellireading-cli.git
> cd intellireading-cli
> pip install .
> intellireading --help
```
### Docker
Alternatively, you can use the Docker image:

#### Help command
```console
> docker pull ghcr.io/0x6f677548/intellireading-cli:latest
> docker run -it --rm ghcr.io/0x6f677548/intellireading-cli --help
```

#### Metaguide an EPUB file
##### Linux/MacOS
```console
```linux
> docker run -it --rm -v $(pwd)/tests:/tests ghcr.io/0x6f677548/intellireading-cli metaguide-epub --input_file '/tests/test_files/input.epub' --output_file '/tests/test_files/output.epub'
```
##### Windows
```powershell
> docker run -it --rm -v ${pwd}/tests:/tests ghcr.io/0x6f677548/intellireading-cli metaguide-epub --input_file '/tests/test_files/input.epub' --output_file '/tests/test_files/output.epub'
```



## Usage
All available commands and options can be seen by using the `--help` option.
```console
> intellireading --help
```

To get help on a specific command, use the `--help` option with the command name. For example, to get help on the `metaguide-epub` command, use the following command:
```console
> intellireading metaguide-epub --help
```

Intellireading is based on [Click](https://github.com/pallets/click/), taking advantage of its features, such as chaining commands and options. 

### Usage Examples

#### Metaguide an EPUB file
To metaguide an EPUB file, use the `metaguide-epub` command. The command requires the path to the EPUB file and the output file. The output file will be a metaguided epub file. 

```console
> intellireading metaguide-epub --input_file mybook.epub --output_file mybook_metaguided.epub
```

#### Metaguide a XHTML file
To metaguide an XHTML file, use the `metaguide-xhtml` command. The command requires the path to the XHTML file and the output file. The output file will be a metaguided xhtml file. 

```console
> intellireading metaguide-xhtml --input_file mybook.xhtml --output_file mybook_metaguided.xhtml
```

#### Metaguide all files in a directory
To metaguide all files in a directory, use the `metaguide-dir` command. The command requires the path to the directory and the output directory. The output directory will contain all metaguided files, including epub, xhtml and html files. 

```console
> intellireading metaguide-dir --input_dir mydir --output_dir mydir_metaguided
```

