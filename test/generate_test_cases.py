import json
import random
from collections import defaultdict

PREREQ_SET_PROBABILITY = 0.4
COREQ_SET_PROBABILITY = 0.3

PREREQ_SET_COUNT_WEIGHTS = [1, 2]
PREREQ_SET_COUNT_WEIGHTS_PROB = [70, 30]

COREQ_SET_COUNT_WEIGHTS = [1, 2]
COREQ_SET_COUNT_WEIGHTS_PROB = [80, 20]

MAX_PREREQ_COREQ_PER_SET = 3
MAX_COURSES_PER_SET = 3
MAX_COUNT_PER_SET = 2

CREDIT_RANGE = (1, 4)


def generate_course_name(index):
    return f"Course_{index}"


def generate_test_case(category_counts):
    all_courses = []
    category_courses = defaultdict(list)
    course_index = 1

    for category, count in category_counts.items():
        for _ in range(count):
            course_name = generate_course_name(course_index)
            credits = random.randint(*CREDIT_RANGE)
            course = {
                "course": course_name,
                "credits": credits,
                "prerequisites": [],
                "corequisites": []
            }
            all_courses.append(course)
            category_courses[category].append(course)
            course_index += 1
    random.shuffle(all_courses)

    for idx, course in enumerate(all_courses):
        if random.random() < PREREQ_SET_PROBABILITY and idx > 0:
            num_prereq_sets = random.choices(
                PREREQ_SET_COUNT_WEIGHTS,
                weights=PREREQ_SET_COUNT_WEIGHTS_PROB
            )[0]
            for _ in range(num_prereq_sets):
                max_possible = min(MAX_PREREQ_COREQ_PER_SET, idx)
                if max_possible < 1:
                    break
                count = random.randint(1, min(MAX_COUNT_PER_SET, max_possible))
                prereq_candidates = [c["course"] for c in all_courses[:idx]]
                if not prereq_candidates:
                    break
                selected_courses = random.sample(
                    prereq_candidates,
                    k=random.randint(
                        1, min(MAX_COURSES_PER_SET, len(prereq_candidates)))
                )
                prerequisite_set = {
                    "count": count,
                    "courses": selected_courses
                }
                course["prerequisites"].append(prerequisite_set)

        if random.random() < COREQ_SET_PROBABILITY and idx > 0:
            num_coreq_sets = random.choices(
                COREQ_SET_COUNT_WEIGHTS,
                weights=COREQ_SET_COUNT_WEIGHTS_PROB
            )[0]
            for _ in range(num_coreq_sets):
                max_possible = min(MAX_PREREQ_COREQ_PER_SET, idx)
                if max_possible < 1:
                    break
                count = random.randint(1, min(MAX_COUNT_PER_SET, max_possible))
                coreq_candidates = [c["course"] for c in all_courses[:idx]]
                if not coreq_candidates:
                    break
                selected_courses = random.sample(
                    coreq_candidates,
                    k=random.randint(
                        1, min(MAX_COURSES_PER_SET, len(coreq_candidates)))
                )
                corequisite_set = {
                    "count": count,
                    "courses": selected_courses
                }
                course["corequisites"].append(corequisite_set)

    json_output = []
    for category, courses in category_courses.items():
        category_obj = {
            "count": len(courses),
            "courses": courses
        }
        json_output.append(category_obj)

    return json_output


def main():
    test_case = generate_test_case()
    print(json.dumps(test_case, indent=4))


if __name__ == "__main__":
    main()
