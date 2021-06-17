

import json
import sys
from pyvis.network import Network


opts_string = json.dumps({
  "nodes": {
    "font": {
      "size": 10
    }
  },
  "edges": {
    "color": {
      "inherit": True
    },
    "smooth": False
  },
  "layout": {
    "hierarchical": {
      "enabled": True,
      "nodeSpacing": 460
    }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
})

infile = sys.argv[1]
outfile = '{}-vis.html'.format(infile)

print ('---- processing: {}'.format(infile))

#print(opts_string)

nt = Network("1500px", "1500px", directed=True)


if(infile.endswith('.gz')):
  print('skipping gz file')
  sys.exit(0)

relationships = []

with open(sys.argv[1]) as fl:

    lines = fl.readlines()
    rewindLine = None

    for l in lines:
      if l.startswith('SPDXID: '):
        spdxid = l.partition(": ")[2].strip()
        name = None
        
        if (rewindLine.startswith('PackageName: ')):
          name = rewindLine.partition(': ')[2].strip()

        nt.add_node(spdxid, label=name, size=10)
        
        #print(spdxid)

      if l.startswith('Relationship: '):
        spdxidFrom = l.split(" ")[1].strip()
        spdxidType = l.split(" ")[2].strip()
        spdxidTo = l.split(" ")[3].strip()
        print(spdxidFrom)
        print(spdxidType)
        print(spdxidTo)

        if spdxidType != 'NONE' and spdxidTo != 'NONE' and spdxidTo != 'NOASSERTION':
          relationships.append( [spdxidFrom, spdxidTo, spdxidType ])

      rewindLine = l
   
    for r in relationships:
      nt.add_edge(r[0], r[1], label=r[2])
      

nt.show_buttons()
#nt.set_options(opts_string)
print("Output: {}".format(outfile))
nt.show(outfile)

