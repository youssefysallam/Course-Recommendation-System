import json
from typing import List, Dict


class Course:
    def __init__(self, code: str, credits: int):
        self.code = code
        self.credits = credits
        self.prerequisites: List[RequisiteGroup] = []
        self.corequisites: List[RequisiteGroup] = []

    def __repr__(self):
        return f"Course(code='{self.code}', credits={self.credits})"


class RequisiteGroup:
    def __init__(self, count: int, courses: List[Course]):
        self.count = count  # Number of courses required from this group
        self.courses = courses

    def __repr__(self):
        course_codes = [course.code for course in self.courses]
        return f'DependencyGroup(count={self.count}, courses={course_codes})'


class ProgramRequirementGroup:
    def __init__(self, count: int, courses: List[Course]):
        self.count = count  # Number of courses required from this group
        self.courses = courses

    def __repr__(self):
        course_codes = [course.code for course in self.courses]
        return f'ProgramRequirementGroup(count={self.count}, courses={course_codes})'


class DependencyGraph:
    def __init__(self, major, data):

        # Maps course codes to Course objects
        self.courses_map: Dict[str, Course] = {}
        self.requirement_groups: List[ProgramRequirementGroup] = []

        if not data:
            with open(f'data/requirements/{major}.json', 'r') as f:
                data = json.load(f)

        # Create Course objects and put them into requirement groups
        for group_data in data:
            group_courses = []
            for course_data in group_data['courses']:
                code = course_data['course']
                credits = course_data['credits']
                course = self.courses_map.get(code)
                if not course:
                    course = Course(code, credits)
                    self.courses_map[code] = course
                group_courses.append(course)
            requirement_group = ProgramRequirementGroup(
                group_data['count'], group_courses)
            self.requirement_groups.append(requirement_group)

        # Resolve prerequisites and corequisites
        for group_data in data:
            for course_data in group_data['courses']:
                course = self.courses_map[course_data['course']]

                # Process prerequisites
                for prereq_group_data in course_data.get('prerequisites', []):
                    prereq_courses = [
                        self.courses_map[code] for code in prereq_group_data['courses']
                    ]
                    prereq_group = RequisiteGroup(
                        prereq_group_data['count'], prereq_courses)
                    course.prerequisites.append(prereq_group)

                # Process corequisites
                for coreq_group_data in course_data.get('corequisites', []):
                    coreq_courses = [
                        self.courses_map[code] for code in coreq_group_data['courses']
                    ]
                    coreq_group = RequisiteGroup(
                        coreq_group_data['count'], coreq_courses)
                    course.corequisites.append(coreq_group)

    def __repr__(self):
        return (f'DependencyGraph(courses={list(self.courses_map.keys())}, '
                f'requirement_groups={self.requirement_groups})')
