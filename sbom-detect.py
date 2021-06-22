import sys
import os
import gzip
import json
import re
import xmltodict
import sbomlib

def traverse(indir):
    sboms = []
    for r, dirs, files in os.walk(indir):
        for f in files:
            path = os.path.join(r, f)
            try: 
                s = sbomlib.BomSniffer(path)
                
                sbom = s.sbom

                if sbom is not None and 'standard' in sbom:
                    sboms.append(s)
                    #print("SBOM: {}::{} ".format(path, sbom))
                else:
                    pass
                    sys.stderr.write("NOTSBOM: {}\n".format(path))

            except Exception as e:
                sys.stderr.write(f"Exception when parsing {path}\n{e}")
                sys.exit(1)

    return sboms

found = traverse(sys.argv[1])
sys.stdout.write(json.dumps(found))

print(" Found: {} SBOMs".format(len(found)))

parsed = []
breakdown = {}

for sbom in found:
    p = None

    k = '{}-{}'.format(sbom.sbom['standard'],sbom.sbom['format'])
    
    if k in breakdown:
        breakdown[k] = breakdown[k] + 1
    else:
        breakdown[k] = 1

    try:
        p = sbom.get_parser()
    except Exception as e:
        print('Error when parsing: {} '.format(sbom.sbom['file']))
        print(e)

    if p is not None:
        parsed.append(p)

print(" Parsed: {} SBOMs".format(len(parsed)))

for k in breakdown:
    print('    {}: {}'.format(k, breakdown[k]))

reports = []
allhashes = {}

for p in parsed:
    reports.append(p.dumpJson())

    hashes = []
    hashes.extend(p.get_all_hashes('SHA-1'))
    hashes.extend(p.get_all_hashes('SHA1'))

    allhashes[p.fileName] = hashes
    #print(' SBOM-file: {} Hashes: {} '.format(p.fileName, hashes))


foundData = []
for f in found:
    foundData.append(f.sbom)

print(' Writing all sboms to sbom-data.json.. ')
with open('sbom-data.json', 'w') as fh:
    json.dump(foundData, fh, indent=4, sort_keys=True)

print(' Writing analysis to sbom-report.json.. ')
with open('sbom-report.json', 'w') as fh:
    json.dump(reports, fh, indent=4, sort_keys=True)

print(' Writing all SHA-1 hashes to sbom-hashes.json.. ')
with open('sbom-hashes.json', 'w') as fh:
    json.dump(allhashes, fh, indent=4, sort_keys=True)


