#users/selectors.py
import csv
from pathlib import Path
from typing import Optional, Dict


def get_university_record(email: str) -> Optional[Dict[str, str]]:
    csv_path = Path(__file__).resolve().parent / "data" / "university_db.csv"

    if not csv_path.exists():
        return None

    with csv_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row.get("email") == email:
                return row

    return None