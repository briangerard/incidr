# incidr
incidr ("insider") - A tool to display IPv4 addresses and netblocks in various formats.

## Motivation

I wrote this for several reasons...

* IPs are stored in various formats in logs, and it can be a pain to translate between
  them.
* Spammers and other bottom-feeders like to obfuscate their IPs to avoid detection, and
  it's handy to have a way to figure out what's really there.
* I'm learning Python, and this was just a bit more complex than many of the programming
  puzzles and tutorials I was finding.  `:)`

## Behavior

A full list of options is available by running `./incidr -h` or `./incidr --help`.

By default, `incidr` will display the given
[CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
"Wikipedia's CIDR page") block in dotted quad, binary, and as hexadecimal and decimal
integers.  Like so:

```
$ ./incidr 10.20.30.40/24
10.20.30.40/24 :
==============
     10. 20. 30. 40 <=> 00001010 00010100 00011110 00101000 <=> 0a141e28 <=> 0169090600
 &  255.255.255.  0 <=> 11111111 11111111 11111111 00000000 <=> ffffff00 <=> 4294967040
 =   10. 20. 30.  0 <=> 00001010 00010100 00011110 00000000 <=> 0a141e00 <=> 0169090560
```

...or...

```
$ ./incidr 10.20.30.40
10.20.30.40 :
===========
   10. 20. 30. 40 <=> 00001010 00010100 00011110 00101000 <=> 0a141e28 <=> 0169090600
```

Most of the options are to limit the display to which specific formats you want.  So
there's `--binary`, `--hexadecimal`, `--decimal`, and `--quad`, which can all be
abbreviated to their minimal prefix (so `--b` is the same as `--binary`).

Multiple CIDR blocks can be specified, with or without netmasks.  There is also a `--mask`
option to specify a netmask which should be applied to all the given IPs.  Multiple
`--mask`s can be given and each mask will be applied in turn.  The masks that are
specified in that way will only be applied to bare IPs, not CIDR blocks which have their
own masks.

The following invocations are all equivalent:
```
$ ./incidr a.b.c.d/m
...
$ ./incidr --mask m a.b.c.d
...
$ ./incidr --mask m --quad --hex --bin --dec a.b.c.d
```

It will also take an IP in one of the alternate forms and re-translate to dotted quad
(along with any or all of the other formats, of course):

```
$ ./incidr 169090600
169090600 :
=========
   10. 20. 30. 40 <=> 00001010 00010100 00011110 00101000 <=> 0a141e28 <=> 0169090600
```


## TODO

* It should really handle IPv6.
* Netmasks are currently only specifiable as mask lengths (1-32).  You should be able to
  use a dotted quad as well.
* Needs a 'minimal' output format, so `incidr --hex 10.20.30.40` just prints `0a141e28`
  and nothing else.

