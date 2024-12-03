class DependencyGraph:
    def __init__(self):
        self.graph = {}

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, from_vertex, to_vertex):
        if from_vertex not in self.graph:
            self.add_vertex(from_vertex)
        if to_vertex not in self.graph:
            self.add_vertex(to_vertex)

        self.graph[from_vertex].append(to_vertex)
