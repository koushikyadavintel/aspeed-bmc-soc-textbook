"""Build the SMBus / I2C / I3C topology deck (20 slides)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from topo_common import Deck
import slides_a, slides_b, slides_c

if __name__ == "__main__":
    d = Deck(footer="SMBus / I2C / I3C Topology  ·  Intel Confidential")
    for part in (slides_a, slides_b, slides_c):
        part.build(d)
    name = sys.argv[1] if len(sys.argv) > 1 else "SMBus_I2C_I3C_Topology_BHS_AVC_OKS.pptx"
    out = os.path.join(HERE, name)
    d.save(out)
    print(f"Wrote {d.n} slides to {out}")
