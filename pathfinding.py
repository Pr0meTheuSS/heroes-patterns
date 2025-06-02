# pathfinding.py
from collections import deque

def get_neighbors(q, r):
    directions = [
        (+1, 0), (+1, -1), (0, -1),
        (-1, 0), (-1, +1), (0, +1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]

def bfs(start, goal, passable_fn):
    queue = deque()
    queue.append((start, [start]))
    visited = set()

    while queue:
        (q, r), path = queue.popleft()
        if (q, r) in visited:
            continue
        visited.add((q, r))

        if (q, r) == goal:
            return path

        for nq, nr in get_neighbors(q, r):
            if passable_fn(nq, nr):
                queue.append(((nq, nr), path + [(nq, nr)]))

    return []
