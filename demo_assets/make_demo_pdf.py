"""Generate demo_assets/ai_architecture_spec.pdf from the .txt spec (valid PDF, real xref offsets)."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
lines = (root / "demo_assets" / "ai_architecture_spec.txt").read_text().splitlines()


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


ops = ["BT", "/F1 10 Tf", "12 TL", "50 760 Td"]
for line in lines:
    ops.append(f"({esc(line)}) Tj T*")
ops.append("ET")
stream = "\n".join(ops).encode("latin-1", "replace")

objs = [
    b"<</Type/Catalog/Pages 2 0 R>>",
    b"<</Type/Pages/Count 1/Kids[3 0 R]>>",
    b"<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
    b"/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>",
    b"<</Length %d>>stream\n" % len(stream) + stream + b"\nendstream",
    b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
]
out = bytearray(b"%PDF-1.4\n")
offsets = []
for i, body in enumerate(objs, 1):
    offsets.append(len(out))
    out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
xref = len(out)
out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
for off in offsets:
    out += b"%010d 00000 n \n" % off
out += b"trailer<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
(root / "demo_assets" / "ai_architecture_spec.pdf").write_bytes(bytes(out))
print("wrote", len(out), "bytes")
