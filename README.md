xsd_expand
==========

Python command line tool and Gedit plugin to quickly show expanded definition of an XSD type

This is a totally alpha release - works only as command line for files in the same directory
and God this is an ugly code... To check that anything works
cd examples
python3 ../xsd_expand.py bbb b.xsd

xsd_expand.py is both cmd line tool and module used by xsd_expand_plugin.py which
is a gedit plugin that when Ctrl-e is pressed in an .xsd file shows the result
of a xsd_expand on variable under cursor

cmd line usage

xsd_expand.py  TypeName file.xsd_Expa

