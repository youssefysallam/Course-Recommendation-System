import csv
import re
import json

file_path = 'data/course_catalog.csv'
output_path = 'data/general_education_courses.json'
attributes = {}


def extract_numeric_part(catalog_nbr):
    match = re.match(r'(\d+)', catalog_nbr)
    return int(match.group(1)) if match else float('inf')


with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
    reader = csv.DictReader(file, delimiter='|')
    for row in reader:
        if row['CTPCS_CRSE_ATTR_VALUE']:
            course = (row['COFFR_SUBJECT'], row['COFFR_CATALOG_NBR'])
            attribute_values = [
                attr.strip() for attr in row['CTPCS_CRSE_ATTR_VALUE'].split(',')
                if attr.strip()
            ]

            for attribute_value in attribute_values:
                if attribute_value not in attributes:
                    attributes[attribute_value] = []
                attributes[attribute_value].append(course)

attributes.pop('Non-degree exclude from list', None)
attributes.pop('Mid-Term Roster course', None)
attributes.pop('Gateway Seminar', None)
attributes.pop('Stay On Track', None)

for attribute, courses in attributes.items():
    attributes[attribute] = sorted(
        courses, key=lambda x: extract_numeric_part(x[1]))

formatted_attributes = {
    attribute: [f"{subject} {catalog_nbr}" for subject, catalog_nbr in courses]
    for attribute, courses in attributes.items()
}

with open(output_path, 'w', encoding='utf-8') as json_file:
    json.dump(formatted_attributes, json_file, indent=4)
