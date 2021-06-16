

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


print(opts_string)

nt = Network("1500px", "1500px", directed=True)

with open(sys.argv[1]) as fl:
    data = json.load(fl)

    for p in data['packages']:
        print(p['SPDXID'])
        nt.add_node(p['SPDXID'], label=p['name'], size=10)

    for r in data['relationships']:
        if(r['relationshipType'] == 'CONTAINS' or r['relationshipType'] == 'DEPENDS_ON'):
            rel = 'D' if r['relationshipType'] == 'DEPENDS_ON' else 'C'

            nt.add_edge(r['spdxElementId'], r['relatedSpdxElement'], label=rel)


nt.show_buttons()
#nt.set_options(opts_string)

nt.show(sys.argv[2])

