#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os.path
import re
import xml.etree.ElementTree as etree

reschema = re.compile('^{http://www.w3.org/2001/XMLSchema}')


def fix_prefix(name):
    return reschema.sub('xsd:', name, 1)


class XSDExpander(object):
    known_types = {'string': {}}
    unknown_types = set()
    schemas2search = set()
    schemas_searched = set()

    def __init__(self):
        pass

    def element_or_attribute(self, el, parent_name, attribute):
        name = ("attribute:" if attribute else "")+el.attrib.get('name')
        type_ = el.attrib.get('type', None)
        if type_:
            if type_.startswith('xsd:'):
                type_ = type_[4:]
            if type_ not in self.known_types:
                self.unknown_types.add(type_)

            minOccurs = el.attrib.get('minOccurs', '')
            self.known_types[parent_name][name] = {
                'name': name,
                'type': type_,
                'minOccurs': minOccurs,
            }
        else:
            print("No type   ----   ", name, el.tag, el.attrib)

    def process_element(self, el, parent_name):
        tag = fix_prefix(el.tag)  # TODO ugly - refactor it  to handlers!
        if tag == 'xsd:annotation':
            return
        elif tag == 'xsd:all':
            for ch in el:
                self.process_element(ch, parent_name)
        elif tag == 'xsd:element':
            self.element_or_attribute(el, parent_name, attribute=False)
        elif tag == 'xsd:attribute':
            self.element_or_attribute(el, parent_name, attribute=True)
        elif tag == 'xsd:include':
            subinc = os.path.normpath(
                os.path.join(
                    os.path.split(self.current_schema)[0],
                    el.attrib['schemaLocation'],
                )
            )
            if subinc not in self.schemas_searched:
                self.schemas2search.add(subinc)
            return

        elif tag in ('xsd:complexType', 'xsd:simpleType'):
            name = el.attrib.get('name')
            if name in self.known_types:
                raise Exception(" Name {0} already defined".format(name))
                self.unknown_types.remove(name)

            self.known_types[name] = {}
            for ch in el:
                self.process_element(ch, name)
        elif tag == 'xsd:restriction':
            type_ = el.attrib.get('base')
            if type_.startswith('xsd:'):
                type_ = type_[4:]
            self.known_types[parent_name][type_] = {
                'name': parent_name,
                'isSimpleType': True,
                'type': type_,
                'minOccurs': '?',
            }
        else:
            print("TAG ", tag)

    def search_schema(self, ):
        tree = etree.parse(self.current_schema)
        root = tree.getroot()
        for child in root:
            self.process_element(child, '/')

    def search(self):
        while self.unknown_types and self.schemas2search:
            inc = self.schemas2search.pop()
            self.schemas_searched.add(inc)
            self.current_schema = inc
            self.search_schema()

    def subshow(self, name, indent):
        if name not in self.known_types:
            print(indent + '     '+name, " nieznane")
        else:
            for k, v in self.known_types[name].items():
                if v.get('isSimpleType', False):
                    print(indent+"    {name} is simple type based on {type}".format(**v))
                else:
                    print(indent+"    {name}={type}({minOccurs})".format(**v))
                    self.subshow(v['type'], indent+'   ')

    def show(self, name):
        print(name)
        self.subshow(name, '')

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 {0} TypeName [schema.xsd]".format(*sys.argv))
        sys.exit(1)
    expander = XSDExpander()
    expander.unknown_types.add(sys.argv[1])
    if len(sys.argv) > 2:
        expander.schemas2search.add(sys.argv[2])
    else:
        expander.schemas2search.add('examples/b.xsd')
    expander.search()
    expander.show(sys.argv[1])
