
import zipfile
from datetime import datetime

class Ev3CompressedFile(object):
    pass

class Ev3ExternalFile(object):
    pass

class Ev3Assets(Ev3CompressedFile):
    pass

class Ev3Program(Ev3CompressedFile):
    pass

class Ev3MyBlock(object):
    pass

class Ev3ProjectDefinition(object):

    def __init__(self, xmldef):
        self.xmldef = xmldef

    def rename(self, old, new):
        pass

    def merge(self, projdef):
        
        for r in roots[1:]:
            self.combine_element(roots[0], r)
        et.register_namespace('', ns[1:-1])
        return et.tostring(roots[0])

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

class Ev3Container(object):

    def __init__(self, filename):
        self.filename = filename
        self.name, _ = os.path.splitext(os.path.basename(filename))
        self.zfile = zipfile.ZipFile(filename)
        self.zdata = 
        
        self.special_patterns = ['Activity.x3a', 'ActivityAssets.laz', 'Project.lvprojx', '__.*']
        self.project_def = Ev3ProjectDefinition.read(self.zfile.open(['Project.lvprojx']))

    def uniquify(self, filename, suffix='_copy'):
        basename, ext = os.path.splitext(filename)
        while filename in self.zfile.namelist():
            basename += suffix
            filename = basename + '.' + ext
        return filename

    def merge(self, ev3):
        for filename in ev3.zfile.namelist():
            if filename in self.special_patterns:
                continue
            
            if filename in self.zfile.namelist():
                if self.zfile.getinfo(filename).CRC == ev3.zfile.getinfo(filename).CRC:
                    continue
                else:
                    new_filename = self.uniquify(filename, suffix='_' + ev3.name)
                    ev3.project_def.rename(filename, new_filename)
                    filename = new_filename

            self.zfile

        self.project_def.merge(ev3.project_def)


    def write(self, filename):
        pass
