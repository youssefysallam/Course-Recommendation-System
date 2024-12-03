import json

REQUIREMENTS_DIR = 'data/requirements'


def get_major():
    major = 'Computer_Science_BS'
    return major


def print_requirements(requirements):
    print('Required courses:')
    required_courses = [required_course['course']
                        for required_course in requirements['required_courses']]
    for course in required_courses:
        print(f'\t{course}')
    choose_courses = requirements['choose_courses']
    for section in choose_courses:
        print(
            f'\t{section["count"]} {section["section_title"]}')


def get_courses_taken():
    courses_taken = ['CS 110', 'MATH 140']
    return courses_taken


def get_requirements(major):
    with open(f'{REQUIREMENTS_DIR}/{major}.json', 'r') as f:
        return json.load(f)


def main():
    major = get_major()
    requirements = get_requirements(major)
    print_requirements(requirements)
    courses_taken = get_courses_taken()


if __name__ == '__main__':
    main()
