import os
import zipfile
from datetime import datetime
from lxml import etree
import re

class Ev3ProjectDefinition(object):

    def __init__(self, xmldef):
        self.xmldef = etree.parse(xmldef)
	#etree.register_namespace('', ns[1:-1])
        
    def rename(self, old, new):
        pass

    def merge(self, projdef):
       	self.combine_element(self.xmldef.getroot(), projdef.xmldef.getroot())
        print etree.tostring(self.xmldef, pretty_print=True)

    def element_repr(self, element):
        attributes = sorted(element.attrib.items())
        return tuple([element.tag] + attributes)
        
    def combine_element(self, one, other):
        one_mapping = {self.element_repr(el): el for el in one}
        other_mapping = {self.element_repr(el): el for el in other}

        for elr in other_mapping:
            if elr in one_mapping:
                self.combine_element(one_mapping[elr], other_mapping[elr])
            else:
                one.append(other_mapping[elr])

    def dump(self):
	return etree.tostring(self.xmldef, pretty_print=True)

class Ev3(object):

    def __init__(self, filename, name=''):
	self.name = name
        self.zfile = zipfile.ZipFile(filename)
        self.zdata = {f: self.zfile.open(f).read() for f in self.zfile.namelist()}

        self.special_patterns = ['Activity.x3a', 'ActivityAssets.laz', 'Project.lvprojx', '__.*']     
        self.project_def = Ev3ProjectDefinition(self.zfile.open('Project.lvprojx'))
	del self.zdata['Project.lvprojx']

    def uniquify(self, filename, suffix='_copy'):
        basename, ext = os.path.splitext(filename)
        while filename in self.zdata:
            basename += suffix
            filename = basename + '.' + ext
        return filename

    def file_is_special(self, filename):
        for pattern in self.special_patterns:
            if re.match(pattern, filename):
                return True
        return False

    def merge(self, ev3):
        for filename in ev3.zdata:
            if self.file_is_special(filename):
                continue
            
            if filename in self.zdata:
                if self.zfile.getinfo(filename).CRC == ev3.zfile.getinfo(filename).CRC:
                    continue
                else:
                    new_filename = self.uniquify(filename, suffix='_' + ev3.name)
                    ev3.project_def.rename(filename, new_filename)
                    filename = new_filename

            self.zdata[filename] = ev3.zdata[filename]
        self.project_def.merge(ev3.project_def)

    def write(self, fileout):
	outfile = zipfile.ZipFile(fileout, 'w')
	for filename in self.zdata:
	    filedata = self.zdata[filename]
	    outfile.writestr(filename, filedata)
	outfile.writestr('Project.lvprojx', self.project_def.dump())
