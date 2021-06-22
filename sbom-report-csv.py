

import json


with open('sbom-report.json') as fh:
    rpt = json.load(fh)

    k = set()

    for row in rpt:
        l = row.keys()
        for kk in l:
            k.add(kk)
    
    
    print(','.join(k))

    for row in rpt:
        d = []
        for c in k:
            if c in row:
                d.append('"' + str(row[c]) + '"')
            else:
                d.append('')
        
        print(','.join(d))