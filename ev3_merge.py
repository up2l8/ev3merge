#!/tool/pandora64/bin/python2.7

import zipfile, os, sys, re

class EV3Merge(object):
    def __init__(self, outfile):
        self.outfile = zipfile.ZipFile(outfile, 'w')
        self.added = {}
        self.special_files = ['Activity.x3a', 'ActivityAssets.laz', 'Project.lvprojx', '__CopyrightYear', '__ProjectTitle']

    def add(self, ev3):
        for filename in ev3.get_file_list():
            handle = ev3.get_file_handle(filename)
            compress_type = ev3.get_info(filename).compress_type
            zinfo = ev3.get_info(filename)
            signature = "%s.%s.%s"%(zinfo.filename, zinfo.file_size, zinfo.CRC)
            data = handle.read()
            if signature in self.added:
                print "INFO: Already added %s with same CRC"%(filename)
                continue

            if filename in self.added and re.search('\.lvprojx$', filename):
                print "WARNING: Skipping %s"%(filename)
                continue

            if filename in self.added:
                newfilename = 'X' + filename
                print "WARNING: Already added %s. Renaming to %s"%(filename, newfilename)
                filename = newfilename

            self.outfile.writestr(filename, data, compress_type=compress_type)
            self.added[signature] = 1
            self.added[filename] = 1

    def handle_special_file(self, filename):
        pass

    def finalize(self):
        pass

class EV3File(object):
    def __init__(self, ev3file):
        self.debug = True
        self.ev3file = ev3file
        self.zfile = zipfile.ZipFile(ev3file)
        if self.debug:
            self.dump_info()

    def get_file_list(self):
        return self.zfile.namelist()

    def get_info(self, filename):
        return self.zfile.getinfo(filename)

    def get_file_handle(self, filename):
        return self.zfile.open(filename)

    def dump_info(self):
        print self.ev3file
        for zinfo in self.zfile.infolist():
            print "  FILE:%s \tSIZE:%d \tCRC:%X \tCOMPRESS:%s"%(zinfo.filename, zinfo.file_size, zinfo.CRC, zinfo.compress_type)

if __name__ == '__main__':
    ev3_1 = EV3File('ArmFunctions.ev3')
    ev3_2 = EV3File('XY_Initialize.ev3')

    merger = EV3Merge('Out.ev3')
    merger.add(ev3_1)
    merger.add(ev3_2)
    merger.finalize()

