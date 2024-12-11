import os
from dependency_graph import DependencyGraph

def TopologicalSort(dependency_graph: DependencyGraph, terms):
    # Initialize dictionaries to track in-degree and adjacency list for courses
    inDegree = {}  # Tracks the number of prerequisites for each course
    adjacencyList = {}  # Tracks which courses depend on a given course
    courseOrder = []  # Holds the sorted order of courses

    # Initialize inDegree and adjacencyList for all courses in the dependency graph
    for course_code, course in dependency_graph.courses.items():
        inDegree[course_code] = 0  # Initially, no prerequisites are assumed
        adjacencyList[course_code] = []  # No dependencies yet

    # Build the graph by populating the adjacency list and in-degree counts
    for course_code, course in dependency_graph.courses.items():
        for prereq_group in course.prerequisites:  # Iterate over prerequisite groups
            for prereq_course in prereq_group.courses:  # Iterate over courses in each group
                adjacencyList[prereq_course.code].append(course_code)  # Add dependency
                inDegree[course_code] += 1  # Increment the in-degree for the dependent course

    # Collect courses with no prerequisites (in-degree = 0) to start the sorting
    queue = [course_code for course_code in dependency_graph.courses if inDegree[course_code] == 0]

    # Process the courses in the queue using Kahn's Algorithm for topological sorting
    while queue:
        current = queue.pop(0)  # Remove the first course in the queue
        courseOrder.append(current)  # Add it to the sorted order

        # Decrease the in-degree of all dependent courses
        for neighbor in adjacencyList[current]:
            inDegree[neighbor] -= 1
            if inDegree[neighbor] == 0:  # If in-degree becomes zero, add to the queue
                queue.append(neighbor)

    # Check if the sorted order includes all courses (i.e., no cycle in the graph)
    if len(courseOrder) != len(dependency_graph.courses):
        raise ValueError("Cycle detected in prerequisites or missing dependency.")

    # Allocate courses to terms in a round-robin fashion
    termAllocation = {term: [] for term in terms}  # Initialize allocation dictionary
    termIndex = 0  # Start with the first term

    for course_code in courseOrder:
        termAllocation[terms[termIndex]].append(course_code)  # Assign course to the current term
        termIndex = (termIndex + 1) % len(terms)  # Move to the next term

    return termAllocation

if __name__ == "__main__":
    major = "computer_science"  # Define the major for which the dependency graph is constructed

    # Dynamically resolve the path to the requirements file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(base_dir, "data", "requirements", f"{major}.json")

    if not os.path.exists(requirements_path):
        print(f"Error: Requirements file not found at {requirements_path}")
    else:
        dependency_graph = DependencyGraph(major)  # Create a dependency graph instance

        terms = ["Fall", "Winter", "Spring"]  # Define available academic terms

        try:
            termAllocation = TopologicalSort(dependency_graph, terms)  # Perform topological sort and allocation
            print("Course allocation by terms:")
            for term, allocatedCourses in termAllocation.items():
                print(f"{term}: {allocatedCourses}")  # Print the allocation for each term
        except ValueError as e:
            print(f"Error: {e}")  # Print error if a cycle or inconsistency is detected
