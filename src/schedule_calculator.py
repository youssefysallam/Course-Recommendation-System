from collections import defaultdict, deque
from typing import Deque, List, Dict, Set
import copy
from dependency_graph import DependencyGraph, ProgramRequirementGroup, Course, RequisiteGroup
import re


class ScheduleCalculator:
    def __init__(self, dependency_graph: DependencyGraph, completed_courses: List[str]):
        self.dependency_graph = copy.deepcopy(dependency_graph)
        self.completed_courses = set(completed_courses)
        self.merged_courses_map = {}
        self.course_to_requirement_groups: Dict[str,
                                                List[ProgramRequirementGroup]] = defaultdict(list)

        self.process_dependency_graph()
        self.sorted_courses = []
        self.topological_sort()
        self.semesters = self.assign_courses_to_semesters()

    def process_dependency_graph(self):
        self.merge_mutual_corequisites()
        self.update_all_dependencies()
        self.treat_corequisites_as_prerequisites()
        self.remove_completed_courses()
        self.update_requirement_groups()
        self.build_course_requirement_mapping()

    def merge_mutual_corequisites(self):
        courses_map = self.dependency_graph.courses_map
        mutual_groups = []
        visited = set()

        for course_code, course in list(courses_map.items()):
            if course_code in visited:
                continue
            mutual_set = self.find_mutual_corequisites(course, courses_map)
            if mutual_set:
                mutual_groups.append(mutual_set)
                visited.update(mutual_set)

        for group in mutual_groups:
            merged_code = '+'.join(sorted(group))
            merged_credits = sum(courses_map[code].credits for code in group)
            merged_course = Course(code=merged_code, credits=merged_credits)

            for code in group:
                course = courses_map[code]
                merged_course.prerequisites.extend(copy.deepcopy(
                    prereq) for prereq in course.prerequisites)
                merged_course.corequisites.extend(
                    copy.deepcopy(coreq) for coreq in course.corequisites)

            for code in group:
                del courses_map[code]

            courses_map[merged_code] = merged_course

            for code in group:
                self.merged_courses_map[code] = merged_code

    def find_mutual_corequisites(self, course: Course, courses_map: Dict[str, Course]) -> Set[str]:
        mutual_set = set()
        to_process = [course.code]

        while to_process:
            current_code = to_process.pop()
            if current_code in mutual_set:
                continue
            mutual_set.add(current_code)
            current_course = courses_map.get(current_code)
            if not current_course:
                continue
            for coreq_group in current_course.corequisites:
                for coreq in coreq_group.courses:
                    coreq_code = coreq.code
                    coreq_course = courses_map.get(coreq_code)
                    if coreq_course and any(c.code == current_code for c in coreq_course.corequisites for _ in []):
                        if coreq_code not in mutual_set:
                            to_process.append(coreq_code)

        mutual_set.discard(course.code)
        if mutual_set:
            mutual_set.add(course.code)
            return mutual_set
        return set()

    def update_all_dependencies(self):
        courses_map = self.dependency_graph.courses_map

        def replace_course_codes(requisite_group: RequisiteGroup, target_course_code: str) -> RequisiteGroup:
            new_courses = []
            removed_courses = 0
            for course in requisite_group.courses:
                merged_code = self.merged_courses_map.get(
                    course.code, course.code)
                if merged_code != course.code:
                    merged_course = courses_map.get(merged_code)
                    if merged_course and merged_code != target_course_code:
                        new_courses.append(merged_course)
                else:
                    if course.code != target_course_code:
                        new_courses.append(course)
                    else:
                        removed_courses += 1
            unique_courses = list({c.code: c for c in new_courses}.values())
            adjusted_count = max(requisite_group.count - removed_courses, 0)
            return RequisiteGroup(count=adjusted_count, courses=unique_courses)

        for course in courses_map.values():
            course.prerequisites = [
                replace_course_codes(prereq_group, course.code)
                for prereq_group in course.prerequisites
                if replace_course_codes(prereq_group, course.code).courses
            ]

            course.corequisites = [
                replace_course_codes(coreq_group, course.code)
                for coreq_group in course.corequisites
                if replace_course_codes(coreq_group, course.code).courses
            ]

    def treat_corequisites_as_prerequisites(self):
        courses_map = self.dependency_graph.courses_map

        for course in courses_map.values():
            for coreq_group in course.corequisites:
                course.prerequisites.append(RequisiteGroup(
                    count=coreq_group.count,
                    courses=copy.deepcopy(coreq_group.courses)
                ))
            course.corequisites = []

    def remove_completed_courses(self):
        courses_map = self.dependency_graph.courses_map

        for completed_code in self.completed_courses:
            courses_map.pop(completed_code, None)

        for course in courses_map.values():
            new_prereq_groups = []
            for prereq_group in course.prerequisites:
                remaining_courses = [
                    c for c in prereq_group.courses if c.code not in self.completed_courses]
                completed_in_group = len(
                    prereq_group.courses) - len(remaining_courses)
                adjusted_count = max(prereq_group.count -
                                     completed_in_group, 0)
                if adjusted_count > 0 and len(remaining_courses) >= adjusted_count:
                    new_prereq_groups.append(RequisiteGroup(
                        count=adjusted_count,
                        courses=remaining_courses
                    ))
            course.prerequisites = new_prereq_groups

    def update_requirement_groups(self):
        for group in self.dependency_graph.requirement_groups:
            remaining_courses = [
                c for c in group.courses if c.code not in self.completed_courses]
            completed_in_group = len(group.courses) - len(remaining_courses)
            group.count = max(group.count - completed_in_group, 0)
            group.courses = remaining_courses

    def build_course_requirement_mapping(self):
        for group in self.dependency_graph.requirement_groups:
            for course in group.courses:
                self.course_to_requirement_groups[course.code].append(group)

    def topological_sort(self):
        courses_map = self.dependency_graph.courses_map
        adjacency_list = defaultdict(list)
        in_degree = defaultdict(int)

        for course_code in courses_map:
            in_degree[course_code] = 0

        for course_code, course in courses_map.items():
            for prereq_group in course.prerequisites:
                for prereq_course in prereq_group.courses:
                    prereq_code = self.merged_courses_map.get(
                        prereq_course.code, prereq_course.code)
                    if prereq_code != course_code:
                        adjacency_list[prereq_code].append(course_code)
                        in_degree[course_code] += 1

        queue: Deque[str] = deque([c for c, d in in_degree.items() if d == 0])
        sorted_order = []

        while queue:
            current = queue.popleft()
            sorted_order.append(current)
            for dependent in adjacency_list[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        self.sorted_courses = sorted_order

    def assign_courses_to_semesters(self) -> List[List[str]]:
        semesters = []
        scheduled_courses = set()
        courses_map = self.dependency_graph.courses_map
        course_prereqs = defaultdict(set)

        for course_code, course in courses_map.items():
            for prereq_group in course.prerequisites:
                for prereq_course in prereq_group.courses:
                    prereq_code = prereq_course.code
                    course_prereqs[course_code].add(prereq_code)

        gen_eds = {c for c in courses_map if not re.search(
            r'\d', c.replace(' ', '').replace('+', ''))}

        total_semesters = max(8, len(courses_map) // 5 + 1)
        semesters = [[] for _ in range(total_semesters)]
        semester_credits = [0 for _ in range(total_semesters)]

        total_gen_eds = len(gen_eds)
        gen_eds_per_semester = total_gen_eds // total_semesters
        extra_gen_eds = total_gen_eds % total_semesters

        gen_ed_list = sorted(gen_eds)
        gen_ed_queue = deque(gen_ed_list)

        for i in range(total_semesters):
            num_gen_ed = gen_eds_per_semester + (1 if i < extra_gen_eds else 0)
            for _ in range(num_gen_ed):
                if gen_ed_queue:
                    gen_ed = gen_ed_queue.popleft()
                    semesters[i].append(gen_ed)
                    semester_credits[i] += courses_map[gen_ed].credits
                    scheduled_courses.add(gen_ed)

        for course_code in self.sorted_courses:
            if course_code in scheduled_courses:
                continue
            for i in range(total_semesters):
                prereqs = course_prereqs[course_code]
                if all(any(prereq in semesters[sem] for sem in range(i)) for prereq in prereqs):
                    if semester_credits[i] + courses_map[course_code].credits <= 15:
                        semesters[i].append(course_code)
                        semester_credits[i] += courses_map[course_code].credits
                        scheduled_courses.add(course_code)
                        break

        remaining_courses = set(courses_map.keys()) - scheduled_courses
        for course_code in remaining_courses:
            for i in range(total_semesters):
                if semester_credits[i] + courses_map[course_code].credits <= 15:
                    semesters[i].append(course_code)
                    semester_credits[i] += courses_map[course_code].credits
                    scheduled_courses.add(course_code)
                    break

        semesters = [sem for sem in semesters if sem]

        return semesters

    def get_semesters(self) -> List[List[str]]:
        return self.semesters

    def get_sorted_courses(self) -> List[str]:
        return self.sorted_courses
