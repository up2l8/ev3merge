#!/tool/pandora64/bin/python2.7

import os, sys, re
import StringIO, zipfile, logging
from xml.etree import ElementTree as et

ns = "{http://www.ni.com/SourceModel.xsd}"  # Fixes the output xmlns Attribute

class EV3Project(object):
    def __init__(self, ev3=None):
        self.special_files = ['Activity.x3a', 'ActivityAssets.laz', 'Project.lvprojx', '__CopyrightYear', '__ProjectTitle']
        self.init_logger()
        self.filedata = {}
        self.fileinfo = {}
        if ev3:
            self.add(ev3)

    def init_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        logger.handlers = []    # Clear existing handlers.
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    def add(self, ev3):
        zfile = zipfile.ZipFile(ev3)
        for filename in zfile.namelist():
            zfh = zfile.open(filename)
            zdata = zfh.read()
            zinfo = zfile.getinfo(filename)

            if filename in self.filedata:
                if zinfo.CRC == self.fileinfo[filename].CRC:
                    logging.debug("Skipping identical file %s"%(filename))
                    continue
                elif filename in self.special_files:
                    zdata = self.merge(filename, self.filedata[filename], zdata)
                    logging.info("Merging files of the same name: %s"%(filename))
                else:
                    logging.warn("Skipping already added file %s"%(filename))
                    continue
#                    filename = self.uniquify(filename)
#                    logging.info("Renamed duplicate file as: %s"%(filename))
            
            logging.debug("Adding file: %s"%(filename))
            self.filedata[filename] = zdata
            self.fileinfo[filename] = zinfo

    def merge(self, filename, data1, data2):
        if re.search('\.lvprojx$', filename):
            return self.merge_lvprojx(data1, data2)
        else:
            return data1

    def merge_lvprojx(self, data1, data2):
        roots = []
        roots.append(et.fromstring(data1))
        roots.append(et.fromstring(data2))
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

    def uniquify(self, filename):
        match = re.match('(\S+)(\.\S+)$', filename)
        if match:
            basename = match.group(1)
            suffix = match.group(2)
        else:
            basename = filename
            suffix = ''

        index = 1
        while True:
            unique_filename = basename + str(index) + suffix
            index += 1
            if unique_filename not in self.filedata:
                break

        return unique_filename
        
    def write(self, ev3):
        outfile = zipfile.ZipFile(ev3, 'w')

        for filename in self.fileinfo:
            data = self.filedata[filename]
            zinfo = self.fileinfo[filename]
            outfile.writestr(filename, data, compress_type=zinfo.compress_type)

if __name__ == '__main__':
    ev3 = EV3Project()
    ev3.add(open('/home/rsmith/tmp/TeamA.ev3', 'r'))
    ev3.add(open('/home/rsmith/tmp/TeamB.ev3', 'r'))
    ev3.write(open('Out.ev3', 'w'))

