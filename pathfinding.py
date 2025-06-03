from collections import deque

def get_neighbors(q, r):
    directions = [
        (+1, 0), (+1, -1), (0, -1),
        (-1, 0), (-1, +1), (0, +1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]

def bfs_to_targets(start, targets, passable_fn, max_depth=50):
    queue = deque()
    queue.append((start, [start]))
    visited = set()

    while queue:
        (q, r), path = queue.popleft()
        if (q, r) in visited:
            continue
        visited.add((q, r))

        if (q, r) in targets:
            return path

        if len(path) > max_depth:
            continue

        for nq, nr in get_neighbors(q, r):
            if (nq, nr) not in visited and passable_fn(nq, nr):
                queue.append(((nq, nr), path + [(nq, nr)]))

    return []

def bfs_with_fallback(start, goal, passable_fn):
    if passable_fn(goal[0], goal[1]):
        return bfs_to_targets(start, {goal}, passable_fn)
    else:
        # Найти соседние клетки к цели, которые проходимы
        candidate_targets = set(
            (q, r) for q, r in get_neighbors(goal[0], goal[1])
            if passable_fn(q, r)
        )
        if not candidate_targets:
            return []  # Вокруг цели всё заблокировано
        return bfs_to_targets(start, candidate_targets, passable_fn)
