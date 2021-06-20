import sys
import os
import gzip
import json
import re
import xmltodict

def try_json(fh):
    try:
        return json.load(fh)
    except Exception as e:
        return None

def try_xml(fh):
    try: 
        return xmltodict.parse(''.join(fh.readlines()))
    except Exception as e:
        return None

def detectfile(infile):
    gzipped = False
    zipfile = False
    info = {}

    with open(infile, 'rb') as test_f:
        gzipped = test_f.read(2) == b'\x1f\x8b'
        test_f.seek(0)
        zipfile = test_f.read(2) == b'\x50\x4b'

    # TODO: Unzip zip file
    if zipfile:
        sys.stderr.write(f"Skipping zipfile: {infile}\n")
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
                        #print(spdxns)
                
                spdxRoot = rdfRoot['{}:SpdxDocument'.format(spdxns)]
                version = spdxRoot['{}:specVersion'.format(spdxns)]

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


def traverse(indir):
    sboms = []
    for r, dirs, files in os.walk(indir):
        for f in files:
            path = os.path.join(r, f)
            try: 
                sbom = detectfile(path)
                if sbom is not None and 'standard' in sbom:
                    sbom['file'] = path
                    sboms.append(sbom)
                else:
                    pass
                    sys.stderr.write("NOTSBOM: {}\n".format(path))

            except Exception as e:
                sys.stderr.write(f"Exception when parsing {path}\n{e}")
                sys.exit(1)

    return sboms

found = traverse(sys.argv[1])
sys.stdout.write(json.dumps(found))

# vim: et nu ts=4
