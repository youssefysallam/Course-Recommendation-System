import csv
import os
from typing import Set

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_HERE, '..', 'data')

_SEMESTER_FILES = {
    'fall_2024':   os.path.join(_DATA, 'fall_2024.csv'),
    'spring_2025': os.path.join(_DATA, 'spring_2025.csv'),
    'winter_2025': os.path.join(_DATA, 'winter_2025.csv'),
}

_cache: dict = {}


def _load(path: str) -> Set[str]:
    courses: Set[str] = set()
    try:
        with open(path, encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                subj = row.get('CLASS_SUBJECT_CD', '').strip().strip('"')
                num  = row.get('CLASS_CATALOG_NBR', '').strip().strip('"')
                if subj and num:
                    courses.add(f'{subj} {num}')
    except FileNotFoundError:
        pass
    return courses


def get_offered_courses(semester_key: str) -> Set[str]:
    if semester_key not in _cache:
        path = _SEMESTER_FILES.get(semester_key, '')
        _cache[semester_key] = _load(path) if path else set()
    return _cache[semester_key]


def available_semesters() -> list:
    return list(_SEMESTER_FILES.keys())
