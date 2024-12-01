import json
import pandas as pd
import os
import glob


def load_course_credits(csv_files):
    combined_df = pd.concat(
        [pd.read_csv(file, sep='|', encoding='latin1', dtype=str)
         for file in csv_files],
        ignore_index=True
    )
    combined_df['COURSE_CODE'] = (
        combined_df['CLASS_SUBJECT_CD'].str.strip().str.upper() + ' ' +
        combined_df['CLASS_CATALOG_NBR'].str.strip()
    )
    return combined_df.set_index('COURSE_CODE')['CRSE_UNITS_MAXIMUM'].to_dict()


def add_credits(courses_list, course_credits):
    updated = []
    for course in courses_list:
        course = course.strip().upper()
        credits = course_credits.get(course, 'N/A')
        if credits != 'N/A':
            credits = int(float(credits))
            updated.append({
                'course': course,
                'credits': credits
            })
    return updated


def process_json_file(json_file_path, course_credits, output_directory):
    json_file_name = os.path.basename(json_file_path)
    with open(json_file_path, 'r', encoding='utf-8', errors='replace') as json_file:
        program_requirements = json.load(json_file)
    if 'required_courses' in program_requirements:
        program_requirements['required_courses'] = add_credits(
            program_requirements['required_courses'], course_credits
        )
    if 'choose_courses' in program_requirements:
        for choice in program_requirements['choose_courses']:
            if 'courses' in choice:
                choice['courses'] = add_credits(
                    choice['courses'], course_credits)
    output_file_path = os.path.join(
        output_directory, f'updated_{json_file_name}')
    with open(output_file_path, 'w', encoding='utf-8', errors='replace') as outfile:
        json.dump(program_requirements, outfile, indent=4)
    print(f'Updated {json_file_name} and saved as updated_{json_file_name}')


def main():
    json_directory = 'data/program_requirements'
    output_directory = 'data/updated_program_requirements'
    os.makedirs(output_directory, exist_ok=True)
    csv_files = [
        'data/fall_2024.csv',
        'data/spring_2025.csv',
        'data/winter_2025.csv'
    ]
    course_credits = load_course_credits(csv_files)
    json_files = glob.glob(os.path.join(json_directory, '*.json'))
    for json_file_path in json_files:
        process_json_file(json_file_path, course_credits, output_directory)
    print('All JSON files have been processed and updated.')


if __name__ == "__main__":
    main()
