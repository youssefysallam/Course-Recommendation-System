import json
from typing import Any


def transform_choose_courses(obj: Any) -> Any:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ['prerequisites', 'corequisites']:
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and 'choose_courses' in item:
                            choose = item['choose_courses']
                            if isinstance(choose, dict):
                                if not choose:
                                    item['choose_courses'] = []
                                else:
                                    item['choose_courses'] = [choose]
                            elif isinstance(choose, list):
                                pass
                            else:
                                pass
            else:
                obj[key] = transform_choose_courses(value)
    elif isinstance(obj, list):
        obj = [transform_choose_courses(element) for element in obj]
    return obj


def process_json(input_json: str) -> str:
    try:
        data = json.loads(input_json)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}")
        return ""

    transformed_data = transform_choose_courses(data)

    return json.dumps(transformed_data, indent=4)


if __name__ == "__main__":
    input_dir = 'data/requirements'
    input_files = [
        'Computer_Engineering_BS.json',
        'Computer_Science_BA.json',
        'Computer_Science_BS.json'
    ]

    for input_file in input_files:
        path = f'{input_dir}/{input_file}'
        with open(path, 'r', encoding='utf-8') as f:
            input_json = f.read()
            output_json = process_json(input_json)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(output_json)
