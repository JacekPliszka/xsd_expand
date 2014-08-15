#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os.path
import xml.etree.ElementTree as etree

class XSDExpander(object):
    known_types={'string':{}}
    unknown_types=set()
    schemas2search=set()
    schemas_searched=set()

    def __init__(self):
        pass

    def search_schema(self, filename):
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
                if subinc not in self.schemas_searched:
                    self.schemas2search.add(subinc)
                continue
            name =  child.attrib.get('name')
            if name not in self.known_types:
                self.known_types[name]={}
                if name in self.unknown_types:
                    self.unknown_types.remove(name)
                for ch in child:
                    child_type = ch.attrib['type']
                    if child_type.startswith('xsd:'):
                        child_type=child_type[4:]
                    child_name = ch.attrib['name']
                    ch.attrib['type'] = child_type
                    self.known_types[name][child_name] = ch.attrib
                    if child_type not in self.known_types:
                        self.unknown_types.add(child_type)

    def search(self):
        while self.unknown_types and self.schemas2search:
            inc = self.schemas2search.pop()
            self.schemas_searched.add(inc)
            self.search_schema(inc)
    
    def subshow(self, name, indent):
        if name not in self.known_types:
            print(indent + '     '+name, " nieznane")
        else:
            for k, v in self.known_types[name].items():
                print(indent+"    {name}={type}({minOccurs})".format(**v))
                self.subshow(v['type'], indent+'   ')

    def show(self, name):
        print(name)
        self.subshow(name, '')

if __name__ == "__main__":
    import sys
    if len(sys.argv)<3:
        print("Usage: python3 {0} TypeName schema.xsd".format(*sys.argv))
        sys.exit(1)
    expander = XSDExpander()
    expander.unknown_types.add(sys.argv[1])
    expander.schemas2search.add(sys.argv[2])
    expander.search()
    expander.show(sys.argv[1])




