def adjacent(ecs, a, b):
    """
    Проверяет, являются ли две сущности соседними по гекс-сетке.
    """
    if not ecs.has(HexPosition, a) or not ecs.has(HexPosition, b):
        return False

    aq, ar = ecs.get(HexPosition, a).q, ecs.get(HexPosition, a).r
    bq, br = ecs.get(HexPosition, b).q, ecs.get(HexPosition, b).r

    directions = [
        (+1, 0), (+1, -1), (0, -1),
        (-1, 0), (-1, +1), (0, +1)
    ]

    for dq, dr in directions:
        if (aq + dq, ar + dr) == (bq, br):
            return True

    return False
