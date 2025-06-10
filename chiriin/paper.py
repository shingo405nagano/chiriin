import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymupdf  # noqa: F401
from matplotlib import pyplot as plt  # noqa: F401
from matplotlib.colors import to_hex  # noqa: F401

from chiriin.config import XY, PaperSize  # noqa: F401

paper_size = PaperSize().portrait_a4_size()
fig, ax = plt.subplots(figsize=(paper_size))
plt.savefig("test.pdf", dpi=300, format="pdf")
