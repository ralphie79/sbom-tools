import sys
import os
import gzip
import json
import re
import xmltodict
#from sbomlib import SpdxJsonSbom, SpdxTvSbom, CdxXmlSbom
import sbomlib


def try_json(fh):
    try:
        js = json.load(fh)

        return js
    except Exception as e:
        return None


def try_xml(fh):
    try: 
        tree = xmltodict.parse(''.join(fh.readlines()))

        return tree
    except Exception as e:
        #print(e)
        return None



def detectfile(infile):

    gzipped = False
    zipfile = False
    info = {}

    with open(infile, 'rb') as test_f:
        gzipped = test_f.read(2) == b'\x1f\x8b'
        
        test_f.seek(0)
        zipfile = test_f.read(2) == b'\x50\x4b'

        info['gzipped'] = gzipped
        info['zipfile'] = zipfile

    # TODO: Unzip zip file
    if zipfile:
        #print ('Skipping zipfile')
        return

    with open(infile, encoding='utf-8') as fl:
        
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
                info['standard'] = 'cdx'
                info['format']  = 'json'
                if 'specVersion' in j:
                    info['version']  = j['specVersion']
            elif 'spdxVersion' in j:
                info['standard'] = 'spdx'
                info['format'] = 'json'
                info['version']  = j['spdxVersion']
            else:
                print("Unknown JSON: {} ".format(j))
        
        # TODO: Make XML work
        if x is not None:
            info['format'] = 'xml'

            if 'SoftwareIdentity' in x: 
                swid = x['SoftwareIdentity']

                info['standard'] = 'swid'
                info['tagId'] = swid['@tagId']
                info['swidVersion'] = swid['@version']

            elif 'SBOM' in x and 'SoftwareIdentity' in x['SBOM']:
                info['standard'] = 'swid-multi'

            elif 'bom' in x:
                info['standard'] = 'cdx'
                #version = x['specVersion']
            elif 'rdf:RDF' in x:
                rdfRoot = x['rdf:RDF']
                spdxns = None
                for ns in rdfRoot:
                    if rdfRoot[ns] == 'http://spdx.org/rdf/terms#':
                        spdxns = ns.replace('@xmlns:', '')
                        print(spdxns)
                
                spdxRoot = rdfRoot['{}:SpdxDocument'.format(spdxns)]
                version = spdxRoot['{}:specVersion'.format(spdxns)]

                #print(spdxRoot)
                #namespace = 
                info['standard'] = 'spdx'
        
        # Check for tag-value
        if x is None and j is None:
            fl.seek(0)

            try: 
                lines = fl.readlines()
                fulldoc = '\n'.join(lines)
                #if 'SPDXVersion: ' in fulldoc:
                m = re.search('SPDXVersion: SPDX-(\d+\.\d+)', fulldoc)
                if m:
                    # tag value
                    info['standard'] = 'spdx'
                    info['format'] = 'tv'
                    info['version'] = m.group(1)
            except UnicodeDecodeError as u:
                # If the file turns out not to be text.. 
                pass

    return info

def try_parse(sbominfo):
    parser = None

    if sbominfo['standard'] == 'spdx':
        if sbominfo['format'] == 'json':
            parser = sbomlib.SpdxJsonSbom(sbominfo['file'])
        elif sbominfo['format'] == 'xml':
            parser = None
        elif sbominfo['format'] == 'tv':
            parser = sbomlib.SpdxTvSbom(sbominfo['file'])
    elif sbominfo['standard'] == 'cdx':
        if sbominfo['format'] == 'xml':
            parser = sbomlib.CdxXmlSbom(sbominfo['file'])
    elif sbominfo['standard'] == 'swid' or sbominfo['standard'] == 'swid-multi':
        parser = None
    
    return parser


def traverse(indir):

    sboms = []

    for r, dirs, files in os.walk(indir):
        for f in files:
            path = os.path.join(r, f)
            #print(path)
            try: 
                sbom = detectfile(path)
                if sbom is not None and 'standard' in sbom:
                    sbom['file'] = path
                    sboms.append(sbom)
                    #print("SBOM: {}::{} ".format(path, sbom))
                else:
                    print("NOTSBOM: {} ".format(path))

            except Exception as e:
                print("Exception when parsing {}".format(path))
                print(e)
                sys.exit(1)

    return sboms



found = traverse(sys.argv[1])

print(" Found: {} SBOMs".format(len(found)))

parsed = []

for sbom in found:
    if 'gzipped' in sbom and sbom['gzipped']:
        continue

    p = try_parse(sbom)
    if p is not None:
        parsed.append(p)

print(" Parsed: {} SBOMs".format(len(parsed)))

reports = []
allhashes = {}

for p in parsed:
    reports.append(p.dumpJson())

    hashes = []
    hashes.extend(p.get_all_hashes('SHA-1'))
    hashes.extend(p.get_all_hashes('SHA1'))

    allhashes[p.fileName] = hashes
    #print(' SBOM-file: {} Hashes: {} '.format(p.fileName, hashes))



print(' Writing all sboms to sbom-data.json.. ')
with open('sbom-data.json', 'w') as fh:
    json.dump(found, fh)

print(' Writing analysis to sbom-report.json.. ')
with open('sbom-report.json', 'w') as fh:
    json.dump(reports, fh)

print(' Writing all SHA-1 hashes to sbom-hashes.json.. ')
with open('sbom-hashes.json', 'w') as fh:
    json.dump(allhashes, fh)


