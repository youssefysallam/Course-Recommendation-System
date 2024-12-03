import json
import copy


def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)


def save_json(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)


def build_course_mapping(main_data):
    course_map = {}

    def add_courses(courses):
        for course in courses:
            course_name = course.get('course')
            if course_name:
                course_map[course_name] = {
                    'credits': course.get('credits'),
                    'prerequisites': course.get('prerequisites', []),
                    'corequisites': course.get('corequisites', [])
                }

    add_courses(main_data.get('required_courses', []))

    for section in main_data.get('choose_courses', []):
        add_courses(section.get('courses', []))

    return course_map


def update_course(course, course_map):
    course_name = course.get('course')
    if course_name and course_name in course_map:
        course_details = copy.deepcopy(course_map[course_name])
        course['credits'] = course_details['credits']
        course['prerequisites'] = course_details['prerequisites']
        course['corequisites'] = course_details['corequisites']


def update_courses_section(section, course_map):
    if 'courses' in section:
        for course in section.get('courses', []):
            update_course(course, course_map)
    else:
        for course in section:
            update_course(course, course_map)


def update_target_json(target_data, course_map):
    update_courses_section(target_data.get('required_courses', []), course_map)

    for section in target_data.get('choose_courses', []):
        update_courses_section(section, course_map)


def main():
    main_json_path = 'data/requirements/Computer_Science_BA.json'
    target_json_paths = ['data/requirements/Computer_Engineering_BS.json',
                         'data/requirements/Computer_Science_BS.json']

    main_data = load_json(main_json_path)

    course_map = build_course_mapping(main_data)

    for target_path in target_json_paths:
        print(f"\nProcessing target JSON: {target_path}")
        target_data = load_json(target_path)

        update_target_json(target_data, course_map)

        save_json(target_data, target_path)


if __name__ == "__main__":
    main()
