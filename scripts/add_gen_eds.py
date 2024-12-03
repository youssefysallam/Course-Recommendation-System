import json
import csv
import os

# Initialize a global dictionary to store course credits
credits_dict = {}


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_csvs(csv_files):
    global credits_dict
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"Warning: {csv_file} does not exist and will be skipped.")
            continue
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                subject_cd = row.get("CLASS_SUBJECT_CD", "").strip()
                catalog_nbr = row.get("CLASS_CATALOG_NBR", "").strip()
                course_code = f"{subject_cd} {catalog_nbr}"
                units_str = row.get("CRSE_UNITS_MAXIMUM", "").strip()
                try:
                    units = int(float(units_str))
                except ValueError:
                    print(
                        f"Warning: Invalid units '{units_str}' for course '{course_code}'. Skipping.")
                    continue
                if course_code not in credits_dict:
                    credits_dict[course_code] = units
                else:
                    if credits_dict[course_code] != units:
                        print(
                            f"Warning: Conflicting credits for course '{course_code}'. Using the first occurrence ({credits_dict[course_code]}).")
    if not credits_dict:
        raise ValueError("No course credits found in the provided CSV files.")


def get_credits(course):
    if course in credits_dict:
        return credits_dict[course]
    else:
        raise KeyError(f"Course '{course}' not found in any of the CSV files.")


def transform_gen_ed_courses(gen_ed_courses):
    transformed = []
    for course in gen_ed_courses:
        try:
            credits = get_credits(course)
        except KeyError as e:
            print(f"Error: {e}")
            credits = 0  # or handle it as per your requirement
        course_dict = {
            "course": course,
            "credits": credits,
            "prerequisites": [],
            "corequisites": []
        }
        transformed.append(course_dict)
    return transformed


def append_gen_ed_to_program(program_requirements, gen_ed_courses):
    for category, courses in gen_ed_courses.items():
        section = {
            "count": 1,
            "section": category,
            "courses": transform_gen_ed_courses(courses)
        }
        program_requirements.append(section)
    return program_requirements


def main():
    program_requirements_file = 'data/requirements/Computer_Science_BS.json'
    gen_ed_courses_file = 'data/general_education_courses.json'
    output_file = 'updated_program_requirements.json'

    csv_files = ['fall_2024.csv', 'winter_2025.csv', 'spring_2025.csv']

    # Load CSVs and populate credits_dict
    load_csvs(csv_files)

    # Load JSON files
    program_requirements = load_json(program_requirements_file)
    gen_ed_courses = load_json(gen_ed_courses_file)

    # Append gen ed courses with credits to program requirements
    updated_program_requirements = append_gen_ed_to_program(
        program_requirements, gen_ed_courses)

    # Save updated program requirements to the output file
    save_json(updated_program_requirements, output_file)

    print(f"Updated program requirements have been saved to '{output_file}'.")
