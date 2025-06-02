import math

def hex_to_pixel(q, r, size):
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 3/2 * r
    return int(x), int(y)

def pixel_to_hex(x, y, size):
    q = (math.sqrt(3)/3 * x - 1/3 * y) / size
    r = (2/3 * y) / size
    return hex_round(q, r)

def hex_round(q, r):
    x = q
    z = r
    y = -x - z
    rx = round(x)
    ry = round(y)
    rz = round(z)

    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return int(rx), int(rz)

def draw_hex(surface, color, center, size, width=0):
    corners = []
    for i in range(6):
        angle = math.pi / 180 * (60 * i + 30)  # ⚠️ сдвиг 30° для "flat-topped"
        dx = center[0] + size * math.cos(angle)
        dy = center[1] + size * math.sin(angle)
        corners.append((dx, dy))
    import pygame
    pygame.draw.polygon(surface, color, corners, width)
