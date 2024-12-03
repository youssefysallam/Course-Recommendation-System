import os
import json
import glob

input_directory = 'data/requirements'

json_files = glob.glob(os.path.join(input_directory, '*.json'))

empty_requirements = [
    {
        "required_courses": [],
        "choose_courses": {}
    }
]


def add_requirements(course):
    course['prerequisites'] = empty_requirements
    course['corequisites'] = empty_requirements


for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if 'required_courses' in data:
        for course in data['required_courses']:
            add_requirements(course)

    if 'choose_courses' in data:
        for elective in data['choose_courses']:
            if 'courses' in elective:
                for course in elective['courses']:
                    add_requirements(course)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
