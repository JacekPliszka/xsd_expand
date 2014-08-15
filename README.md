xsd_expand
==========

Python command line tool and Gedit plugin to quickly show expanded definition of an XSD type

This is a totally alpha release - works only as command line
and God this is an ugly code...

xsd_expand.py is both cmd line tool and module used by xsd_expand_plugin.py which
is a gedit plugin that when Ctrl-e is pressed in an .xsd file shows the result
of a xsd_expand on variable under cursor

cmd line usage

    xsd_expand.py  TypeName file.xsd

E.g.

    python3 xsd_expand.py bbb examples/b.xsd
