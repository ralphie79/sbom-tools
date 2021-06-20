

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

print(opts_string)

nt = Network("1500px", "1500px", directed=True)


if(infile.endswith('.gz')):
  print('skipping gz file')
  sys.exit(0)

with open(sys.argv[1]) as fl:

    data = json.load(fl)

    if 'packages' not in data:
        print('- file does not have packages')
        sys.exit(1)
      
    if 'relationships' not in data:
        print('- file does not have relationships')
        sys.exit(1)

    if 'files' not in data:
        print('- file does not have files (not fatal)')
    #else:
      #for f in data['files']:
          #nt.add_node(f['SPDXID'], label=f['fileName'], size=5)

    for p in data['packages']:
        nt.add_node(p['SPDXID'], label=p['name'], size=10)

    for r in data['relationships']:
        if(r['relationshipType'] == 'CONTAINS' or r['relationshipType'] == 'DEPENDS_ON'):
            rel = 'D' if r['relationshipType'] == 'DEPENDS_ON' else 'C'
            try: 
              nt.add_edge(r['spdxElementId'], r['relatedSpdxElement'], label=rel)
            except Exception as e:
              # do nothing print('-error adding node: {}'.format(e))
              pass


nt.show_buttons()
nt.set_options(opts_string)

print("Output: \"{}\"".format(outfile))
nt.show(outfile)

