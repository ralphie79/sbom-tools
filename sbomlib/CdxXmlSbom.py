
from typing import OrderedDict
import xmltodict

from .GenericSbom import GenericSbom
from .SbomTypes import * 

class CdxXmlSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None
    fileName = None


    def unwindHashes(self, hashes):
        ret = []

        for h in hashes['hash']:
            r = Hash()
            r.algo = h['@alg']
            r.value = h["#text"]
            ret.append(r)
        
        return ret


    def nodeToPackage(self, pkg):
        p = Package()
        
        if '@bom-ref' in pkg:
            p.id = pkg['@bom-ref']
        
        if 'purl' in pkg:
            p.id = pkg['purl']

        p.name = pkg['name']

        if 'version' in pkg:
            p.version = pkg['version']
        
        if 'publisher' in pkg:
            p.supplierName = pkg['publisher']
        
        if 'hashes' in pkg:
            p.hashes = self.unwindHashes(pkg['hashes'])

        p.rawdata = pkg
        
        return p
        

    def nodeToRelationship(self, rel):

        ret = None

        if 'dependency' in rel:
            ret = []
            if isinstance(rel['dependency'], OrderedDict):
                r = Relationship()

                r.fromId = rel['@ref']
                r.toId = rel['dependency']['@ref']
                r.type = 'cdx-dep'

                ret.append(r)
            else: 
                for d in rel['dependency']:
                    r = Relationship()

                    r.fromId = rel['@ref']
                    r.toId = d['@ref']
                    r.type = 'cdx-dep'

                    ret.append(r)

        return ret

    def nodeToFile(self, fil):
        pass


    def __init__(self, infile):
        
        self.fileName = infile

        with open(infile) as fh:
            data = xmltodict.parse(''.join(fh.readlines()))


            if 'bom' in data:
                bom = data['bom']
                #ref = data['bom']['@bom-ref']

                if 'components' in data['bom']:
                    comps = data['bom']['components']
                    complist = comps['component']
                    self.packages = []

                    if isinstance(complist, OrderedDict):
                        self.packages.append(self.nodeToPackage(complist))
                    else:
                        for c in complist:
                            self.packages.append(self.nodeToPackage(c))
                        
                if 'metadata' in bom:
                    
                    md = bom['metadata']
                    fp = FinalProduct()

                    fp.name = md['component']['name']

                    if 'timestamp' in md:
                        fp.creationDate = md['timestamp']
                    
                    if 'authors' in md:
                        if isinstance(md['authors'], list):
                            nn = ''
                            for n in md['authors']['author']:
                                nn = nn + ' ' + n['name']
                            fp.sbomAuthor = nn
                    
                    if 'component' in md:
                        fp.name = md['component']['name']
                        if 'purl' in md['component']:
                            fp.id = md['component']['purl']
                    
                    if 'supplier' in md:
                        fp.supplierName = md['supplier']['name']
                    
                    self.product = fp

                if 'dependencies' in bom:
                    self.relationships = []
                    depsnode = bom['dependencies']
                    depslist = depsnode['dependency']

                    if isinstance(depslist, OrderedDict):
                        nr = self.nodeToRelationship(depslist)
                        for r in nr:
                            self.relationships.append(r)
                    else: 
                        for dep in depslist:
                            nr = self.nodeToRelationship(dep)
                            for r in nr:
                                self.relationships.append(r)
                
                if 'files' in bom:
                    self.files = []
                    print('has files')

