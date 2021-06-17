import sys
import os
import gzip
import json
import xml.etree.ElementTree as ET
import lxml.etree

def try_json(fh):
    try:
        js = json.load(fh)

        return js
    except Exception as e:
        return None


def try_xml(fh):

    try: 
        #tree = ET.parse(fh)

        tree = lxml.etree.parse(fh)

        return tree

    except Exception as e:
        print(e)
        return None


def detectfile(infile):

    standard = None
    format = None
    version = None
    gzipped = False
    zipfile = False

    with open(infile, 'rb') as test_f:
        gzipped = test_f.read(2) == b'\x1f\x8b'
        test_f.seek(0)
        zipfile = test_f.read(2) == b'\x50\x4b'

    if zipfile:
        print ('Skipping zipfile')
        return

    with open(infile) as fl:
        
        j = None

        if gzipped:
            with gzip.open(infile) as fh:
                j = try_json(fh)
                fh.seek(0)
                x = try_xml(fh)
        else:
            j = try_json(fl)
            fl.seek(0)
            x = try_xml(fl)


        if j is not None:
            if 'bomFormat' in j:
                standard = 'cdx'
                format = 'json'
                if 'specVersion' in j:
                    version = j['specVersion']
            elif 'spdxVersion' in j:
                standard = 'spdx'
                format = 'json'
                version = j['spdxVersion']
            else:
                print("Unknown JSON: {} ".format(j))
        
        if x is not None:
            format = 'xml'

            root = x.xpath('//SoftwareIdentity')

            print(root)
        
        if x is None and j is None:
            fl.seek(0)

            lines = fl.readlines()
            fulldoc = ''.join(lines)
            if 'SPDXVersion: ' in fulldoc:
                # tag value
                standard = 'spdx'
                format = 'tv'
                version = 'XXX'


    if standard is not None:
        print("FOUND: {} - {} {} {} ".format(infile, standard, format, version)) 


def traverse(indir):

    for r, dirs, files in os.walk(indir):
        for f in files:
            path = os.path.join(r, f)
            print(path)
            detectfile(path)


traverse(sys.argv[1])

