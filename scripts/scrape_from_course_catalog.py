import re
import json
import requests
from bs4 import BeautifulSoup


PROGRAM_URLS = [
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13888/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13786/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13785/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13958/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=14487/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13787/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13788/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13789/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13791/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13896/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13794/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13793/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13798/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13906/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13836/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13837/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13838/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13841/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13842/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13843/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13775/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13897/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13799/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13801/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13800/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13802/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13852/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13853/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13829/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13893/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13894/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13872/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13976/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13848/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13846/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13845/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13844/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13961/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13887/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13804/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13803/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13796/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13816/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13784/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13797/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13957/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13805/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13903/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13847/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13849/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13909/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13885/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13891/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13898/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13889/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13963/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13962/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13851/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13937/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13871/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13776/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13777/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13890/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13938/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13874/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13901/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13808/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13809/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13939/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13899/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13875/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13951/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13914/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13900/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13810/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13955/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13956/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13778/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13949/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13876/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13877/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13806/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13895/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13811/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13773/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13918/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13866/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13966/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13967/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13855/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13812/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13813/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13792/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13867/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13869/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13821/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13819/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13817/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13820/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13818/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13856/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13857/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13858/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13822/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13823/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13960/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13859/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13771/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13825/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13827/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13828/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13824/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13975/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13972/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13774/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13902/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13904/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13832/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13833/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13892/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13807/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13779/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13964/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13950/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13814/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13815/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13834/',
    'https://catalog.umb.edu/preview_program.php?catoid=54&poid=13835/'
]

OUTPUT_JSON_FILE = 'data/program_requirements.json'


def fetch_html_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_program(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract program name
    program_name_tag = soup.find('h1', id='acalog-content')
    program_name = program_name_tag.get_text(
        strip=True) if program_name_tag else 'Unknown Program'

    required_courses = []
    choose_courses = []

    # Find all course requirement sections
    course_sections = soup.find_all('div', class_='acalog-core')

    for section in course_sections:
        course_list_items = section.find_all('li', class_='acalog-course')
        if not course_list_items:
            # Skip sections that don't contain courses
            continue

        heading_tag = section.find(['h2', 'h3'])
        if not heading_tag:
            continue
        section_title = heading_tag.get_text(strip=True)

        section_title_clean = re.sub(r'\s*\(.*?\)', '', section_title).strip()

        # Determine if the section is elective or required
        if is_elective_section(section_title_clean):
            instruction_text = section.get_text(strip=True)
            count = extract_course_count(instruction_text)

            courses = extract_courses_from_section(section)

            choose_courses.append({
                'count': count or len(courses),
                'courses': courses
            })
        else:
            courses = extract_courses_from_section(section)
            required_courses.extend(courses)

    program_data = {
        'program_name': program_name,
        'required_courses': required_courses,
        'choose_courses': choose_courses
    }

    return program_data


def extract_courses_from_section(section):
    courses = []
    course_list_items = section.find_all('li', class_='acalog-course')
    for item in course_list_items:
        course_link = item.find('a')
        if course_link:
            course_text = course_link.get_text(strip=True)
            course_code = course_text.split(' - ')[0]
            courses.append(course_code)
    return courses


def extract_course_count(text):
    match = re.search(r'(Take|Select|Choose|Complete)\s+(\w+)', text)
    if not match:
        return None

    count_word = match.group(2)
    number_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
        'nine': 9, 'ten': 10
    }
    return number_map.get(count_word.lower())


def is_elective_section(title):
    elective_keywords = ['Elective', 'Choose',
                         'Select', 'Options', 'Electives']
    return any(keyword.lower() in title.lower() for keyword in elective_keywords)


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")


def main():
    all_programs_data = []

    for index, url in enumerate(PROGRAM_URLS, start=1):
        print(f"\nProcessing URL {index}/{len(PROGRAM_URLS)}: {url}")
        html_content = fetch_html_content(url)
        if html_content:
            program_data = parse_program(html_content)
            all_programs_data.append(program_data)

            print(json.dumps(program_data, indent=4))
        else:
            print(f"Skipping URL due to fetch error: {url}")

    save_to_json(all_programs_data, OUTPUT_JSON_FILE)


if __name__ == "__main__":
    main()
