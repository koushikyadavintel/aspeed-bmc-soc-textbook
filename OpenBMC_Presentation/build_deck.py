"""Build OpenBMC_Architecture.pptx from the slide modules."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck_helpers import Deck
import slides_part1, slides_part2, slides_part3, slides_part4, slides_part5, slides_part6

if __name__ == "__main__":
    d = Deck()
    for part in (slides_part1, slides_part2, slides_part3, slides_part4, slides_part5, slides_part6):
        part.build(d)
    name = sys.argv[1] if len(sys.argv) > 1 else "OpenBMC_Architecture.pptx"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    d.save(out)
    print(f"Wrote {d.n} slides to {out}")
