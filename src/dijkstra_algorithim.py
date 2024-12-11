import heapq
import json
import argparse
from dependency_graph import DependencyGraph


def dijkstra(courses, start):
    priorty_queue = []
    # Initializes all distances to infinity except the start node, which is srt to 0.
    distances = {course: float('inf') for course in courses}
    distances[start] = 0
    previous_nodes = {course: None for node in courses}
    # Adds start node initialized to distance = 0.
    heapq.heappush(priorty_queue, (0, start))

    while priorty_queue:
        current_distance, current_course = heapq.heappop(priorty_queue)

        if current_distance > distances[current_course]:
            continue

        # Processes all prereq groups for current selected course.
        for prereq_group in courses[current_course].prerequisites:
            for prereq_course in prereq_group.courses:
                distance = current_distance + 1
                if distance < distances[prereq_course.code]:
                    distances[prereq_course.code] = distance
                    previous_nodes[prereq_course.code] = current_course
                    heapq.heappush(
                        priorty_queue, (distance, prereq_course.code))
        return distances, previous_nodes


# Here the function is used to suggest cources that can be taken next based on completed prereqs.
def recommend_courses(course, completed_courses):
    recommend = []
    for course in courses.values():
        if course.code not in completed_courses:
            if all(  # Check to see if all prereq groups have at least 1 completed course, thus enabling the current course to be recommended.
                any(prereq.code in completed_courses for prereq in prereq_group.courses)
                for prereq_group in course.prerequisites
            ):
                recommend.append(course.code)
        return recommend

    def main():
        # Setting up command-line arguments to specify the major and completed courses.
        parser = argparse.ArgumentParser(
            description="Course Recommendation System")
        parser.add_argument("--major", type=str, required=True,
                            help="The major to load requirements for.")
        parser.add_argument("--completed", type=str, nargs="*",
                            default=[], help="List of completed courses.")

        args = parser.pare_args()
        # Load the dependency graph
        with open(args.graph, "r") as graph_file:
            graph = json.load(graph_file)

        # Convert the loaded graph into Course objects
        courses = {course_code: Course(
            course_code, data["credits"]) for course_code, data in graph.items()}
        for course_code, data in graph.items():
            for prereq_group in data["prerequisites"]:
                courses[course_code].prerequisites.append(
                    DependencyGraph(prereq_group["count"], [
                                    courses[prereq] for prereq in prereq_group["courses"]])
                )

        completed_courses = set(args.completed)

        next_courses = recommend_courses(graph.courses, completed_courses)
        print("Recommended courses for next semester:", next_courses)

        if __name__ == "__main__":
            main()
