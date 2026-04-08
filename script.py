with open("UECFOOD256\category.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

names = []

for line in lines[1:]:  # skip header
    parts = line.strip().split("\t")
    if len(parts) >= 2:
        names.append(parts[1])

with open("data.yaml", "a", encoding="utf-8") as f:
    for name in names:
        f.write(f"  - {name}\n")

print("✅ data.yaml created successfully")