from dependency_graph import DependencyGraph


def get_major():
    major = 'Computer_Science_BS'
    return major


def main():
    major = get_major()
    graph = DependencyGraph(major)
    print(graph)


if __name__ == '__main__':
    main()
