
from GenericSbom import GenericSbom
import json
import SbomTypes

class SpdxTvSbom(GenericSbom):

    packages = None
    files = None
    relationships = None
    product = None

    def consumeFile(self, fil):
        f = SbomTypes.File()

        f.name = fil['FileName']

        f.id = fil['SPDXID']

        for a in ['MD5', 'SHA1', 'SHA256']:
            if a in fil:
                if f.hashes is None:
                    f.hashes = []
                h = SbomTypes.Hash()
                h.algo = a
                h.value = fil[a]
                f.hashes.append(h)
        
        return f


    def consumePackage(self, pkg):
        p = SbomTypes.Package()
        
        p.id = pkg['SPDXID']
        p.name = pkg['PackageName']

        if 'PackageVersion' in pkg:
            p.version = pkg['PackageVersion']
        
        if 'PackageSupplier' in pkg:
            p.supplierName = pkg['PackageSupplier']
        
        if 'PackageChecksum' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = SbomTypes.Hash()
            h.algo = 'SHA1' # default type
            h.value = pkg['PackageChecksum']
            p.hashes.append(h)
        
        if 'MD5' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = SbomTypes.Hash()
            h.algo = 'MD5' 
            h.value = pkg['MD5']
            p.hashes.append(h)

        if 'SHA1' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = SbomTypes.Hash()
            h.algo = 'SHA1' 
            h.value = pkg['SHA1']
            p.hashes.append(h)

        if 'SHA256' in pkg:
            if p.hashes is None:
                p.hashes = []
            h = SbomTypes.Hash()
            h.algo = 'SHA256' 
            h.value = pkg['SHA256']
            p.hashes.append(h)

        return p
        



    def __init__(self, infile):
        self.fileName = infile

        with open(infile) as fh:
            inTextTag = False
            fragment = {}
            fragments = []
            lastk = None

            for ln in fh.readlines():
                if not ln.startswith("#"):
                    ln = ln.strip()
                    
                    if(len(ln) == 0 and not inTextTag):
                        if len(fragment) > 0:
                            fragments.append(fragment)
                        fragment = {}
                        continue

                    if not inTextTag:
                        if ':' in ln:
                            k, v = ln.split(':',1)

                            v = v.strip()



                            if k == 'Relationship':
                                if self.relationships == None:
                                    self.relationships = []

                                r = SbomTypes.Relationship()
                                r.fromId, r.type, r.toId = v.split(' ', 2)

                                self.relationships.append(r)

                            elif k == 'PackageChecksum' or k == 'FileChecksum':
                                if ':' in v:
                                    algo, value = v.split(':')
                                    fragment[algo] = value.strip()
                            elif k == 'PackageVerificationCode':
                                if ':' in v:
                                    algo, value = v.split(':')
                                    fragment[algo] = value.strip()
                                else:
                                    fragment['SHA1'] = v.strip()
                            else:
                                fragment[k] = v
                                lastk = k

                            if '<text>' in v:
                                inTextTag = True
                        else:
                            # assume continuation of last entry
                            fragment[lastk] = fragment[lastk] + " " + ln    

                    else:
                        fragment[lastk] = fragment[lastk] + " " + ln
                        if '</text>' in v:
                            inTextTag = False

                else:
                  if(len(fragment)> 0):
                    fragments.append(fragment)

            
            if(len(fragment)> 0):
                fragments.append(fragment)

            for frag in fragments:
                if 'PackageName' in frag:
                    if self.packages == None:
                        self.packages = []

                    self.packages.append(self.consumePackage(frag))
                
                if 'FileName' in frag:
                    if self.files == None:
                        self.files = []

                    self.files.append(self.consumeFile(frag))

                




        

if __name__ == '__main__':
    
    x = SpdxTvSbom('inputs/Tern/simple_container/hello_world_linux_spdxtagvalue.txt')

    x = SpdxTvSbom('inputs/Cisco/Snort30/example-snort30.spdx')

    x = SpdxTvSbom('inputs/Anchore/dir_serve/serve.spdx')

    x  = SpdxTvSbom('inputs/aDolus - FACT/node/spdx/NodeExt.zip.spdx')

    x.dump()

