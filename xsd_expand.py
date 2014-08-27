#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os.path
import re
import xml.etree.ElementTree as etree
from uuid import uuid4
from pprint import pprint as pp

reschema = re.compile('^{http://www.w3.org/2001/XMLSchema}')


def fix_prefix(name):
    return reschema.sub('xsd:', name, 1)


class XSDExpander(object):
    known_types = {'string': {}, '/': {}}
    groups = {}
    unknown_types = set()
    schemas2search = set()
    schemas_searched = set()

    def __init__(self):
        pass

    def first_unused_tag(self, fmt):
		# TODO migrate to uuid or something else
        for i in range(1000000):
            type_ = fmt.format(i)
            if type_ not in self.known_types and type_ not in self.unknown_types:
                return type_
        raise Exception("More than 1000000 iterations")

    def element_or_attribute(self, el, parent, parent_name, attribute):
        name = ("attribute:" if attribute else "")+el.attrib.get('name')
        type_ = el.attrib.get('type', None)
        if not type_:
            # Below deals with anonymount complexType   element name=x  <xomplexType> <something>
            if len(el) == 1 and el[0]:
                subtag = fix_prefix(el[0].tag)
                if subtag == 'xsd:complexType':
                    type_ = self.first_unused_tag("__{}__{}".format(name, "{}"))
                    self.unknown_types.add(type_)
                    el[0].set('name', type_)
                    self.process_element(el[0], type_, parent_name)
        if type_:
            if type_.startswith('xsd:'):
                type_ = type_[4:]
            if type_ not in self.known_types:
                self.unknown_types.add(type_)

            minOccurs = el.attrib.get('minOccurs', '')
            parent[name] = {
                'name': name,
                'type': type_,
                'minOccurs': minOccurs,
            }
        else:
            print("No type   ----   ", name, el.tag, el.attrib)
            import pdb; pdb.set_trace()

    def process_element(self, el, parent, parent_name):
        tag = fix_prefix(el.tag)  # TODO ugly - refactor it  to handlers!
        if tag == 'xsd:annotation':
            return
        elif tag in ('xsd:all', 'xsd:sequence'):
            for ch in el:
                self.process_element(ch, parent, parent_name)
        elif tag == 'xsd:element':
            self.element_or_attribute(el, parent, parent_name, attribute=False)
        elif tag == 'xsd:attribute':
            self.element_or_attribute(el, parent, parent_name, attribute=True)
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
                self.process_element(ch, self.known_types[name], name)
        elif tag == 'xsd:restriction':
            type_ = el.attrib.get('base')
            if type_.startswith('xsd:'):
                type_ = type_[4:]
            parent[type_] = {
                'name': parent_name,
                'isSimpleType': True,
                'type': type_,
                'minOccurs': '?',
            }
        elif tag == 'xsd:group':
            name = el.attrib.get('name')
            ref = el.attrib.get('ref')
            if name:
                print(tag, name)
                self.groups[name] = {}
                for ch in el:
                    # TODO possible bug here as parent_name is lost and 'group:name' appears
                    self.process_element(ch, self.groups[name], 'group:'+name)
            elif ref:
                parent[uuid4()] = {
                    'isGroup': True,
                    'ref': ref
                }
            else:
                raise Exception('group with no name and no ref')
        else:
            print("TAG ", tag)

    def search_schema(self, ):
        #print(self.current_schema)
        tree = etree.parse(self.current_schema)
        root = tree.getroot()
        for child in root:
            self.process_element(child, self.known_types['/'], '/')

    def search(self):
        while self.unknown_types and self.schemas2search:
            inc = self.schemas2search.pop()
            self.schemas_searched.add(inc)
            self.current_schema = inc
            self.search_schema()

    def subshow_element(self, v, indent):
        if v.get('isSimpleType', False):
            print(indent+"    {name} is simple type based on {type}".format(**v))
        if v.get('isGroup', False):
            self.subshow_group(v['ref'], indent)
        else:
            print(indent+"    {name}={type}({minOccurs})".format(**v))
            self.subshow(v['type'], indent+'   ')

    def subshow_group(self, name, indent):
        for v in self.groups[name].values():
            self.subshow_element(v, indent)

    def subshow(self, name, indent):
        if name not in self.known_types:
            print(indent + '     '+name, " nieznane")
        else:
            for v in self.known_types[name].values():
                self.subshow_element(v, indent)

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
