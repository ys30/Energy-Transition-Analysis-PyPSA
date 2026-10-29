from pathlib import Path
import argparse
from .analysis import analyze
p=argparse.ArgumentParser()
p.add_argument("--output",default="outputs")
a=p.parse_args()
print(analyze(Path(a.output)))
