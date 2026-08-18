from pathlib import Path
import json
from collections import defaultdict

p = Path("DATASET/True_data/qualitative_corpus/processed_chunks/MDA_BOARD_combined.jsonl")

records = [
    json.loads(line)
    for line in p.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

groups = defaultdict(list)

for record in records:
    groups[record["text"].strip()].append(record)

duplicates = [
    group for group in groups.values()
    if len(group) > 1
]

print("DUPLICATE TEXT GROUPS:", len(duplicates))

for i, group in enumerate(duplicates, 1):
    print(f"\n--- DUPLICATE GROUP {i} ---")

    for record in group:
        print(
            f"Chunk ID       : {record['chunk_id']}\n"
            f"Category       : {record['category']}\n"
            f"Document       : {record['document_name']}\n"
            f"Section        : {record['section_title']}\n"
            f"Text           : {record['text'][:1000]}\n"
        )
