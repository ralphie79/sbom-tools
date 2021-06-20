import sys
import os
import json
import xml 
import traceback

#process SPDX using the python lib
def parseSPDX(item):
    from spdx.parsers.loggers import StandardLogger
    format = item['format']
    try:
        if format == 'json':
            from spdx.parsers.jsonparser import Parser
            from spdx.parsers.jsonyamlxmlbuilders import Builder
        elif format == 'xml':
            from spdx.parsers.xmlparser import Parser
            from spdx.parsers.jsonyamlxmlbuilders import Builder
        elif format == 'tv':
            from spdx.parsers.tagvalue import Parser
            from spdx.parsers.tagvaluebuilders import Builder
        else:
            item['error'] = f"SPDX {format} not supported using lib parser"
        parser = Parser(Builder(), StandardLogger())
        with open(item['file'], 'r') as f:
            (sbom, error) = parser.parse(f)
            if error:
                raise RuntimeError(error)
            item['name'] = doc.package.name
    except Exception as e:
        item['error'] = traceback.format_exc()
    return item 

#process some SPDX formats by hand
def parseSPDXRaw(item):
    format = item['format']
    try:
        sbom = None
        if format == 'json':
            with open(item['file'], 'r') as f:
                sbom = json.load(f)
                item['name'] = sbom['name']
        #elif format == 'xml':
        #    pass
        else:
            item['error'] = f"SPDX {format} not supported in raw parser"
    except Exception as e:
        item['error'] = traceback.format_exc()
    return item

#process some CDX formats by hand
def parseCDX(item):
    format = item['format']
    try:
        sbom = None
        if format == 'json':
            with open(item['file'], 'r') as f:
                sbom = json.load(f)
                try:
                    item['name'] = sbom['metadata']['component']['name']
                except KeyError as e:
                    item['name'] = "no parent name"
        #elif format == 'xml':
        #    pass
        else:
            item['error'] = f"CDX {format} not supported"
    except Exception as e:
        item['error'] = traceback.format_exc()
    return item


#expect input as json array of {file, standard, format, version} dicts
src = (open(sys.argv[1], 'r') if len(sys.argv) == 2 else sys.stdin)
sboms = []
try:
    sboms = json.load(src)
except Exception as e:
    sys.stderr.write(f"invalid input: {e}")
    sys.exit(1)

parsedSBOMs = []
for sbom in sboms:
    if sbom['standard'] == "spdx":
        #todo: fix SPDX parsing, many errors
        #sbom = parseSPDX(sbom)
        sbom = parseSPDXRaw(sbom)
    elif sbom['standard'] == "cdx":
        sbom = parseCDX(sbom)
    elif sbom['standard'] == "swid":
        pass
    elif sbom['standard'] == "swid-multi":
        pass
    else:
        sbom['error'] = "unsupported sbom standard"
    parsedSBOMs.append(sbom)

#write back updated json sbom array
sys.stdout.write(json.dumps(parsedSBOMs))

# vim: et nu ts=4
