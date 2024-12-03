import json
import csv

csv_files = [
    'data/fall_2024.csv',
    'data/spring_2025.csv',
    'data/winter_2025.csv'
]

input_json_file = 'data/all_general_education_courses.json'
output_json_file = 'data/new_general_education_courses.json'


def build_course_dict(csv_files):
    course_dict = {}
    for csv_file in csv_files:
        with open(csv_file, mode='r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                subject_cd = row.get('CLASS_SUBJECT_CD', '').strip()
                catalog_nbr = row.get('CLASS_CATALOG_NBR', '').strip()
                prereq = row.get('COFFR_PRE_REQ_LDESC', '').strip()
                credits_str = row.get('CRSE_UNITS_MAXIMUM', '').strip()
                course_name = f"{subject_cd} {catalog_nbr}"

                if course_name:
                    # Convert credits to int, handle possible conversion errors
                    try:
                        credits = int(float(credits_str))
                    except ValueError:
                        print(
                            f"Invalid credits '{credits_str}' for course '{course_name}'. Setting credits to 0.")
                        credits = 0

                    if course_name not in course_dict or not course_dict[course_name]:
                        course_dict[course_name] = {
                            'prereq': prereq,
                            'credits': credits
                        }
    return course_dict


def process_general_education_courses(input_file, output_file, course_dict):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modified = False
    output_data = []

    for section_title, courses in data.items():
        if not isinstance(courses, list):
            print(
                f"'courses' is not a list in section '{section_title}'. Skipping this section.")
            continue

        original_course_count = len(courses)
        filtered_courses = []
        removed_count = 0

        for course_code in courses:
            course_code = course_code.strip()
            if course_code in course_dict:
                prereq = course_dict[course_code]['prereq']
                if not prereq or 'First Year Seminar' in prereq or 'Intermediate Seminar' in prereq:
                    filtered_courses.append(course_code)
                else:
                    print(
                        f"Removing course '{course_code}' from section '{section_title}' because it has prerequisites: '{prereq}'")
                    removed_count += 1
            else:
                # Course not found in course_dict; remove it
                print(
                    f"Removing course '{course_code}' from section '{section_title}' because it is not found in the course dictionary.")
                removed_count += 1

        if removed_count > 0:
            data[section_title] = filtered_courses
            modified = True
            print(
                f"Updated section '{section_title}': {removed_count} course(s) removed.")

        # Build the gen ed category structure
        gen_ed_category = {
            "count": len(filtered_courses),
            "courses": []
        }

        for course_code in filtered_courses:
            course_info = course_dict.get(course_code, {})
            credits = course_info.get('credits', 0)

            course_entry = {
                "course": course_code,
                "credits": credits,
                "prerequisites": [],
                "corequisites": []
            }
            gen_ed_category["courses"].append(course_entry)

        output_data.append(gen_ed_category)

    if modified:
        print(f"\nChanges detected. Building the new JSON structure.")
    else:
        print("\nNo changes detected. Building the JSON structure based on input data.")

    # Save the output data as a JSON array
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        print(f"Saved updated JSON file to: {output_file}")


def main():
    print("Building course dictionary from CSV files...")
    course_dict = build_course_dict(csv_files)
    print(f"Total courses loaded: {len(course_dict)}")

    print("\nProcessing general education courses...")
    process_general_education_courses(
        input_json_file, output_json_file, course_dict)
    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
