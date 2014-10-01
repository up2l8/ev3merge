import os
import zipfile
from datetime import datetime
from lxml import etree

class Ev3ProjectDefinition(object):

    def __init__(self, xmldef):
        self.xmldef = etree.parse(xmldef)
	#etree.register_namespace('', ns[1:-1])
        
    def rename(self, old, new):
        pass

    def merge(self, projdef):
       	self.combine_element(self.xmldef.getroot(), projdef.xmldef.getroot())

    def combine_element(self, one, other):
        mapping = {el.tag: el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    # Update the text
                    mapping[el.tag].text = el.text
                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[el.tag] = el
                    # Add it
                    one.append(el)
            else:
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[el.tag], el)
                except KeyError:
                    # Not in the mapping
                    mapping[el.tag] = el
                    # Just add it
                    one.append(el)

    def dump(self):
	return etree.tostring(self.xmldef, pretty_print=True)

class Ev3(object):

    def __init__(self, filename, name=''):
	self.name = name
        self.zfile = zipfile.ZipFile(filename)
	self.zdata = dict([(f, self.zfile.open(f).read()) for f in self.zfile.namelist()])
        
        self.special_patterns = ['Activity.x3a', 'ActivityAssets.laz', 'Project.lvprojx', '__.*']
        self.project_def = Ev3ProjectDefinition(self.zfile.open('Project.lvprojx'))
	del self.zdata['Project.lvprojx']

    def uniquify(self, filename, suffix='_copy'):
        basename, ext = os.path.splitext(filename)
        while filename in self.zfile.namelist():
            basename += suffix
            filename = basename + '.' + ext
        return filename

    def merge(self, ev3):
        for filename in ev3.zdata:
            if filename in self.special_patterns:
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
