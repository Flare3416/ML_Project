from pathlib import Path


# Approximate kcal per serving. Items missing here will use DEFAULT_CALORIES.
BASE_CALORIES_DB = {
	"rice": 130,
	"beef curry": 180,
	"sushi": 150,
	"fried rice": 163,
	"tempura bowl": 220,
	"toast": 265,
	"croissant": 406,
	"roll bread": 270,
	"hamburger": 295,
	"pizza": 266,
	"sandwiches": 250,
	"udon noodle": 127,
	"soba noodle": 99,
	"ramen noodle": 188,
	"fried noodle": 214,
	"spaghetti": 158,
	"gratin": 170,
	"miso soup": 40,
	"omelet": 154,
	"fried chicken": 246,
	"steak": 271,
	"potato salad": 143,
	"green salad": 50,
	"macaroni salad": 160,
	"hot dog": 290,
	"french fries": 312,
	"pancake": 227,
	"tiramisu": 283,
	"waffle": 291,
	"shortcake": 346,
	"bagel": 250,
	"tacos": 226,
	"nachos": 346,
	"lasagna": 135,
	"caesar salad": 190,
	"muffin": 377,
	"popcorn": 387,
	"cream puff": 335,
	"doughnut": 452,
	"apple pie": 237,
	"parfait": 245,
	"adobo": 250,
	"brownie": 466,
	"churro": 447,
	"jambalaya": 174,
	"nasi goreng": 168,
	"laksa": 200,
	"mie goreng": 208,
	"kaya toast": 310,
	"chow mein": 155,
	"kung pao chicken": 242,
	"baked salmon": 208,
	"hot & sour soup": 91,
	"ice cream": 207,
	"cake": 257,
	"burger": 295,
	"noodles": 138,
	"salad": 50,
}

# Fallback used when a class exists in category.txt but has no specific entry above.
DEFAULT_CALORIES = 200


def _category_file_path() -> Path:
	return Path(__file__).resolve().parents[1] / "UECFOOD256" / "category.txt"


def _read_category_names(category_path: Path) -> list[str]:
	if not category_path.exists():
		return []

	lines = category_path.read_text(encoding="utf-8").splitlines()
	names: list[str] = []

	for line in lines[1:]:
		parts = line.split("\t", 1)
		if len(parts) != 2:
			continue
		names.append(parts[1].strip())

	return names


def _build_calories_db() -> dict[str, int]:
	category_names = _read_category_names(_category_file_path())

	calories_db: dict[str, int] = {}
	for name in category_names:
		key = name.lower()
		calories_db[name] = BASE_CALORIES_DB.get(name, BASE_CALORIES_DB.get(key, DEFAULT_CALORIES))

	return calories_db


CALORIES_DB = _build_calories_db()


def calculate_calories(detections: list[dict]) -> tuple[int, list[dict]]:
	total = 0
	details = []

	for item in detections:
		food = str(item.get("food", "")).strip()
		if not food:
			continue

		cal = CALORIES_DB.get(food)
		if cal is None:
			cal = BASE_CALORIES_DB.get(food.lower(), DEFAULT_CALORIES)

		total += cal
		details.append({
			"food": food,
			"calories": cal,
		})

	return total, details
