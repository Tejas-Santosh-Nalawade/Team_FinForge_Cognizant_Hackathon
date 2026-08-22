from pathlib import Path

ROOT = Path("DATASET/True_data/qualitative_corpus")
MDNA = ROOT / "MD&A"
BOARD = ROOT / "Board_Oversight_Memos"

print("MD&A + BOARD OVERSIGHT SOURCE CORPUS")
print("=" * 60)

for folder, label in [(MDNA, "MD&A"), (BOARD, "BOARD OVERSIGHT")]:
    files = sorted(folder.glob("*.txt"))

    print(f"\n{label}: {len(files)} source documents")

    for f in files:
        text = f.read_text(encoding="utf-8")
        print(f"  {f.name} | {len(text)} characters")

print("\nSOURCE CORPUS CHECK COMPLETE")
print("All documents are synthetic test data and non-authoritative.")
