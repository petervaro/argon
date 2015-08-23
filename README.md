argon
=====

*Powerful and Flexible Argument Handler*

Description
-----------

`argon` is a powerful and super flexible CLI argument parser. It can almost
handle any type of interface schemas. Some of its characteristics:

- it can handle boolean flags, flags with single values, flags with value arrays
  (values both repeated or unique) and flags with named values (key-value pairs)
- it can handle nested flags (contexts)
- it has an easy to use, very dynamic and lasy declarative style
- it has a unified parsed return value, but also provides several traverse
  functions for easier argument/value checking
- it has a tiny, but powerful text-templating system to build help texts
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
