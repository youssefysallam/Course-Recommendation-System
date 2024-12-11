import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.append(src_dir)


import time
import matplotlib.pyplot as plt
from dependency_graph import DependencyGraph
from schedule_calculator import ScheduleCalculator
from generate_test_cases import generate_test_case


def measure_schedule_calculator_time(num_courses, num_categories=5):
    courses_per_category = num_courses // num_categories
    category_counts = {
        f"Category_{i+1}": courses_per_category for i in range(num_categories)}

    remainder = num_courses % num_categories
    for i in range(remainder):
        category = f"Category_{i+1}"
        category_counts[category] += 1

    test_case_data = generate_test_case(category_counts)

    start_time = time.time()
    dependency_graph = DependencyGraph(major="test_major", data=test_case_data)
    dependency_graph_time = time.time() - start_time

    completed_courses = []
    start_time = time.time()
    ScheduleCalculator(dependency_graph, completed_courses)
    schedule_calculator_time = time.time() - start_time

    total_time = dependency_graph_time + schedule_calculator_time
    return total_time


def main():
    course_counts = list(range(50, 1050, 50))
    running_times = []

    for num_courses in course_counts:
        print(f"Measuring running time for {num_courses} courses...")
        time_taken = measure_schedule_calculator_time(num_courses)
        running_times.append(time_taken)
        print(f"Time taken: {time_taken:.4f} seconds")

    plt.figure(figsize=(12, 6))
    plt.plot(course_counts, running_times,
             marker='o', linestyle='-', color='b')
    plt.title('ScheduleCalculator Running Time vs. Number of Courses')
    plt.xlabel('Number of Courses')
    plt.ylabel('Running Time (seconds)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('schedule_calculator_running_time.png')
    plt.show()


if __name__ == "__main__":
    main()
