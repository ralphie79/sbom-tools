
import json
import re
from terminaltables import AsciiTable

counts = {}


def do_inc(val):
    global counts

    if val in counts:
        counts[val] = counts[val] + 1
    else:
        counts[val] = 1



with open('sbom-hashes.json') as fh:
    rpt = json.load(fh)

    for k in rpt.keys():
        v = rpt[k]

        for h in v:
            do_inc(h)


fr = {}

for c in sorted(counts.items(), key=lambda x: x[1]):
    if c[1] > 1:
        fr[c[0]] = 1

        print("{}: {}".format(c[0], c[1]))
    
print (' -- unwind')

newfr = {}

for x in rpt:
    for k in fr:
        if rpt[x] is not []:
            if k in rpt[x]:
                if k not in newfr:
                    newfr[k] = []
                newfr[k].append(x)
    

print ('Total hashes: {}'.format(len(counts)))
print (' -- unwind fr')

for r in newfr:
    prodlist = newfr[r]
    npl = set()
    for p in prodlist:
        producer = re.match(r'inputs/(.+?)/', p)
        if producer:
            npl.add(producer.group(1))

    
    if len(npl) > 1:
        print("{}: {}".format(r, npl))


