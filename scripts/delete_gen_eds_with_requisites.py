import os
import json
import csv

csv_files = [
    'data/fall_2024.csv',
    'data/spring_2025.csv',
    'data/winter_2025.csv'
]
json_input_directory = 'data/requirements'
json_output_directory = 'data/updated_program_requirements'

target_section_titles = {
    "United States",
    "International",
    "World Cultures",
    "Social & Behavioral Sciences",
    "Humanities",
    "The Arts",
    "World Languages",
    "Natural Sciences",
    "Mathematics and Technology"
}


def build_course_dict(csv_files):
    course_dict = {}
    for csv_file in csv_files:
        try:
            with open(csv_file, mode='r', encoding='latin-1') as f:
                reader = csv.DictReader(f, delimiter='|')
                for row in reader:
                    subject_cd = row.get('CLASS_SUBJECT_CD', '').strip()
                    catalog_nbr = row.get('CLASS_CATALOG_NBR', '').strip()
                    prereq = row.get('COFFR_PRE_REQ_LDESC', '').strip()
                    course_name = f"{subject_cd} {catalog_nbr}"
                    if course_name:
                        if course_name not in course_dict or not course_dict[course_name]:
                            course_dict[course_name] = prereq
        except FileNotFoundError:
            print(f"CSV file not found: {csv_file}")
        except Exception as e:
            print(f"Error processing CSV file {csv_file}: {e}")
    return course_dict


def process_json_files(input_dir, output_dir, course_dict, target_section_titles):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                modified = False

                choose_courses = data.get('choose_courses')
                if not choose_courses:
                    print(
                        f"No 'choose_courses' section found in {filename}. Skipping.")
                else:
                    if isinstance(choose_courses, dict):
                        choose_courses = [choose_courses]
                    elif not isinstance(choose_courses, list):
                        print(
                            f"'choose_courses' is neither a list nor a dict in {filename}. Skipping.")
                        choose_courses = []

                    for section in choose_courses:
                        section_title = section.get(
                            'section_title', '').strip()
                        if section_title in target_section_titles:
                            courses = section.get('courses', [])
                            if not isinstance(courses, list):
                                print(
                                    f"'courses' is not a list in section '{section_title}' of {filename}. Skipping this section.")
                                continue

                            original_course_count = len(courses)
                            filtered_courses = []
                            removed_count = 0

                            for course in courses:
                                course_code = course.get('course', '').strip()
                                if course_code in course_dict:
                                    if not course_dict[course_code]:
                                        filtered_courses.append(course)
                                    else:
                                        # Course has prerequisites; remove it
                                        print(
                                            f"Removing course '{course_code}' from section '{section_title}' in {filename} because it has prerequisites: '{course_dict[course_code]}'")
                                        removed_count += 1
                                else:
                                    # Course not found in course_dict; remove it
                                    print(
                                        f"Removing course '{course_code}' from section '{section_title}' in {filename} because it is not found in the course dictionary.")
                                    removed_count += 1

                            if removed_count > 0:
                                section['courses'] = filtered_courses
                                modified = True
                                print(
                                    f"Updated section '{section_title}' in {filename}: {removed_count} course(s) removed.")

                if modified:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                        print(f"Saved updated JSON file to: {output_path}")
                else:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(
                        f"No changes made to {filename}. Copied original to output directory.")

            except json.JSONDecodeError:
                print(f"Invalid JSON format in file: {filename}. Skipping.")
            except Exception as e:
                print(f"Error processing JSON file {filename}: {e}")


def main():
    print("Building course dictionary from CSV files...")
    course_dict = build_course_dict(csv_files)
    print(f"Total courses loaded: {len(course_dict)}")

    print("\nProcessing JSON files...")
    process_json_files(json_input_directory, json_output_directory,
                       course_dict, target_section_titles)
    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
