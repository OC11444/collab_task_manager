"""
Users module selectors.

Author: Mich omolo

This file holds read-only lookup logic for user-related data.

Why this exists:
Instead of mixing file-reading logic into views, serializers, or models,
the module keeps external user verification in one place. That makes the
users module easier to maintain and gives the app one clear place to check
whether an email exists in the university record.
"""

import csv
from pathlib import Path
from typing import Optional, Dict


def get_university_record(email: str) -> Optional[Dict[str, str]]:
    """
    Return a matching university record for the given email.

    Why this matters:
    During signup or account approval, the system may need to confirm that
    a person belongs to the university before creating or activating a user.
    This function supports that business rule by checking the local university
    data source and returning the matching row when it exists.

    Args:
        email: The university email address being checked.

    Returns:
        A dictionary containing the matched university record if the email
        exists in the CSV file. Returns None if the file is missing or if
        no matching record is found.

    Business logic:
    - Build the path to the university data file inside the users module.
    - Stop early if the file does not exist, since validation cannot happen
      without the source data.
    - Read the CSV as structured rows so each column can be accessed by name.
    - Compare the stored email value against the provided email.
    - Return the first matching record because one email should represent
      one university identity.
    """
    csv_path = Path(__file__).resolve().parent / "data" / "university_db.csv"

    if not csv_path.exists():
        return None

    with csv_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row.get("email") == email:
                return row

    return None