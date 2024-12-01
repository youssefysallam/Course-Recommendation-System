import json
import os

general_education_file_path = 'data/general_education_courses.json'
program_requirements_directory = 'data/program_requirements'


def add_general_education_requirements(program_file):
    with open(program_file, 'r') as pf:
        program_data = json.load(pf)

    with open(general_education_file_path, 'r') as gf:
        general_education_data = json.load(gf)

    general_education_requirements = [
        {"section_title": "United States", "count": 1,
            "courses": general_education_data.get("United States", [])},
        {"section_title": "International", "count": 1,
            "courses": general_education_data.get("International", [])},
        {"section_title": "Arts", "count": 1,
            "courses": general_education_data.get("Arts", [])},
        {"section_title": "Humanities", "count": 1,
            "courses": general_education_data.get("Humanities", [])},
        {"section_title": "Social & Behavioral Sciences", "count": 2,
            "courses": general_education_data.get("Social & Behavioral Sciences", [])},
        {"section_title": "Natural Sciences", "count": 1,
            "courses": general_education_data.get("Natural Sciences", [])},
        {"section_title": "Mathematics and Technology", "count": 1,
            "courses": general_education_data.get("Mathematics and Technology", [])},
        {"section_title": "First Year Seminar", "count": 1,
            "courses": general_education_data.get("First Year Seminar", [])},
        {"section_title": "Intermediate Seminar", "count": 1,
            "courses": general_education_data.get("Intermediate Seminar", [])}
    ]

    if "choose_courses" not in program_data:
        program_data["choose_courses"] = []

    program_data["choose_courses"].extend(general_education_requirements)

    with open(program_file, 'w') as pf:
        json.dump(program_data, pf, indent=4)


def process_all_program_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            program_file_path = os.path.join(directory, filename)
            add_general_education_requirements(program_file_path)


process_all_program_files(
    program_requirements_directory)
