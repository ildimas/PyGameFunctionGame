import random
def wallsgen(window_width, window_height, wall_length, space_factor, wall):
    tiles = window_width // wall_length
    holes = tiles // space_factor
    
    current_iteration = 1
    for i in range(1, tiles + 1):
        if current_iteration != i:
            continue
        if holes != 0 and random.randint(1, 2) == 1:
            space_tiles = random.randint(1, holes)
            holes -= space_tiles
            current_iteration += space_tiles
            continue
        wall.append([(wall_length * i), window_height])
        current_iteration += 1

wall = []
wallsgen(400, 800, 20, 3, wall)
print(wall)
        