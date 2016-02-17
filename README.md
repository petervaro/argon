[![[license: GPLv3]][1]][2]
[![[python: 3.5.1]][3]][4]

- - -

![argon][5]

*Powerful and Flexible Argument Handler*

Description
-----------

`argon` is a powerful and super flexible CLI argument parser. It can handle
almost any type of interface schemes. Some of its characteristics:

- it can handle:
    - boolean flags,
    - flags with optional or mandatory single values,
    - flags with optional or mandatory value arrays
      (values both repeated or unique),
    - flags with optional or manadatory named values (key-value pairs)
    - flags and values not separated by space
    - flags and values separated by user defined delimiter
    - flags grouping
    - *double-dash* like end-of-parameters flag
- it can handle optional or mandatory nested flags (contexts)
- it can handle program name aliases (build different behaviour inside the same
  program with different program names)
- it has an easy to use, very dynamic and lazy declarative style
- it has a unified parsed return value, but also provides several traverse
  functions for easier argument + value + members checking
- it has a tiny, but powerful text-templating system to build reusable help
  texts
- it has very informative errors, and optionally it can handle those errors as
  well
- almost everything is customizable about it


Dependencies
------------

- [dagger](https://github.com/petervaro/dagger)
- [orderedset](https://github.com/petervaro/orderedset)

> ***NOTE:*** If you have `bash` and `git` installed on your system, you can run
> `install.sh` and it will download the dependencies for you, and install argon
> as well.


Installation
------------

On Linux and Macintosh:

```
$ git clone https://github.com/petervaro/argon.git
$ cd argon
$ bash install.sh
```


Usage
-----

*Work-In-Progress (check ./doc/Exxx.py files for examples)*


License
-------

Copyright &copy; 2015-2016 **Peter Varo**

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program, most likely a file in the root directory, called 'LICENSE'.
If not, see <http://www.gnu.org/licenses>.

- - -

The font used in the logo is called **Kelson Sans**. It is licensed under the
[Fontfabric Free Font EULA v2.0](http://www.fontfabric.com/about).

Copyright &copy; 2012 **Bruno Mello**

<!-- -->

[1]: https://img.shields.io/badge/license-GNU_General_Public_License_v3.0-blue.svg
[2]: http://www.gnu.org/licenses/gpl.html
[3]: https://img.shields.io/badge/python-3.5.1-lightgrey.svg
[4]: https://docs.python.org/3
[5]: img/logo.png?raw=true "Argon"
