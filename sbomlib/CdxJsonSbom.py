
from typing import OrderedDict
import json

from .GenericSbom import GenericSbom
from .SbomTypes import * 

class CdxJsonSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None
    fileName = None



    def __init__(self, infile):
        
        self.fileName = infile


        with open(infile) as fh:
            data = json.load(fh)

            if 'components' in data:
                self.packages = []
                for c in data['components']:
                    p = Package()
                    
                    if 'bom-ref' in c:
                        p.id = c['bom-ref']
                    elif 'purl' in c:
                        p.id = c['purl']

                    p.name = c['name']
                    
                    if 'publisher' in c:
                        p.supplierName = c['publisher']

                    p.version = c['version']
                    self.packages.append(p)

            if 'metadata' in data:
                md = data['metadata']
                mdc = md['component']
                fp = FinalProduct()

                if 'bom-ref' in mdc:
                    fp.id = mdc['bom-ref']
                elif 'purl' in mdc:
                    fp.id = mdc['purl']

                fp.name = mdc['name']

                if 'timestamp' in md:
                    fp.creationDate = md['timestamp']
                                    
                fp.supplierName = mdc['supplier']['name']

                for auth in md['authors']:
                    fp.sbomAuthor = auth['name']

                self.product = fp

            
            if 'dependencies' in data:
                deps = data['dependencies']
                self.relationships = []

                for d in deps:
                    for to in d['dependsOn']:
                        r = Relationship()
                        r.fromId = d['ref']
                        r.toId = to
                        r.type = 'dependsOn'

                        self.relationships.append(r)

                    




