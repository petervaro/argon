argon
=====

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
    - flags and values separated by special character sequence
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
