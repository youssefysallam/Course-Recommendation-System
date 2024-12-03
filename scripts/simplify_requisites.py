import json


def flatten_requisites(path):
    with open(path, 'r') as f:
        course_data = json.load(f)

    def flatten_requisite_list(requisites):
        flattened = []
        for requisite in requisites:
            if "required_courses" in requisite and requisite["required_courses"]:
                flattened.append({
                    "count": len(requisite["required_courses"]),
                    "courses": requisite["required_courses"]
                })
            if "choose_courses" in requisite and requisite["choose_courses"]:
                for choice in requisite["choose_courses"]:
                    flattened.append({
                        "count": choice["count"],
                        "courses": choice["courses"]
                    })
        return flattened

    for entry in course_data:
        for course in entry.get("courses", []):
            if "prerequisites" in course:
                course["prerequisites"] = flatten_requisite_list(
                    course["prerequisites"])

            if "corequisites" in course:
                course["corequisites"] = flatten_requisite_list(
                    course["corequisites"])

    with open(path, 'w') as f:
        json.dump(course_data, f)


def main():
    paths = [
        'data/requirements/Computer_Engineering_BS.json',
        'data/requirements/Computer_Science_BA.json',
        'data/requirements/Computer_Science_BS.json'
    ]

    for path in paths:
        flatten_requisites(path)


if __name__ == "__main__":
    main()
