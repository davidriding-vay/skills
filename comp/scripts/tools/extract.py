import sys
import fitz

if len(sys.argv) != 3:
    sys.exit("usage: python3 extract.py <input.pdf> <output.txt>")
doc = fitz.open(sys.argv[1])
with open(sys.argv[2], "w", encoding="utf-8") as out:
    for i, p in enumerate(doc, 1):
        out.write(f"\n=====PAGE {i}=====\n{p.get_text()}")
print(len(doc))
