#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import os.path
import xml.etree.ElementTree as etree

known_types={'string':{}}
unknown=set()
includes_unknown=set()
includes_searched=set()

def search(filename):
    global known_types, unknown, includes_unknown, includes_searched
    #print '=====Searching for {} in  {}'.format(tag, filename)
    tree = etree.parse(filename)
    root = tree.getroot()
    for child in root:
        if child.tag == '{http://www.w3.org/2001/XMLSchema}include':
            subinc = os.path.normpath(
                os.path.join(
                    os.path.split(filename)[0],
                    child.attrib['schemaLocation'],
                )
            )
            if subinc not in includes_searched:
                includes_unknown.add(subinc)
            continue
        name =  child.attrib.get('name')
        if name not in known_types:
            known_types[name]={}
            if name in unknown:
                unknown.remove(name)
            for ch in child:
                child_type = ch.attrib['type']
                if child_type.startswith('xsd:'):
                    child_type=child_type[4:]
                child_name = ch.attrib['name']
                ch.attrib['type'] = child_type
                known_types[name][child_name] = ch.attrib
                if child_type not in known_types:
                    unknown.add(child_type)

def show(name, indent):
    if name not in known_types:
        print(indent + '    '+name, " nieznane")
    else:
        for k, v in known_types[name].items():
            print(indent+"    {name}={type}({minOccurs})".format(**v))
            show(v['type'], indent+'     ')

import sys
name=sys.argv[1]
includes_unknown.add(sys.argv[2])
unknown.add(name)

while unknown and includes_unknown:
    inc = includes_unknown.pop()
    includes_searched.add(inc)
    search(inc)


print(name)
show(name, '')

# python3 go.py bbb b.xsd



