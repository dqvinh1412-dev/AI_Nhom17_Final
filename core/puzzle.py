import random


GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
GRID_SIZE = 4


def get_blank_index(state):
    """Return the index of the empty tile, represented by 0."""
    return state.index(0)


def can_move(state, index):
    """Check whether the tile at index can move into the blank cell."""
    blank_index = get_blank_index(state)
    blank_row, blank_col = divmod(blank_index, GRID_SIZE)
    tile_row, tile_col = divmod(index, GRID_SIZE)

    row_distance = abs(blank_row - tile_row)
    col_distance = abs(blank_col - tile_col)

    return row_distance + col_distance == 1


def move_tile(state, index):
    """Move a tile if possible and return the new state."""
    if not can_move(state, index):
        return state

    blank_index = get_blank_index(state)
    new_state = list(state)
    new_state[blank_index], new_state[index] = new_state[index], new_state[blank_index]
    return tuple(new_state)


def get_neighbors(state):
    """Return all states that can be reached by one valid move."""
    blank_index = get_blank_index(state)
    blank_row, blank_col = divmod(blank_index, GRID_SIZE)
    neighbors = []

    possible_positions = [
        (blank_row - 1, blank_col),
        (blank_row + 1, blank_col),
        (blank_row, blank_col - 1),
        (blank_row, blank_col + 1),
    ]

    for row, col in possible_positions:
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            tile_index = row * GRID_SIZE + col
            neighbors.append(move_tile(state, tile_index))

    return neighbors


def get_neighbors_with_actions(state):
    """Return valid moves as (move_name, new_state) pairs.

    The move name describes the direction of the blank tile. For example,
    "Move Right" means the blank tile swaps with the tile on its right.
    """
    blank_index = get_blank_index(state)
    blank_row, blank_col = divmod(blank_index, GRID_SIZE)
    moves = [
        ("Move Up", blank_row - 1, blank_col),
        ("Move Down", blank_row + 1, blank_col),
        ("Move Left", blank_row, blank_col - 1),
        ("Move Right", blank_row, blank_col + 1),
    ]
    neighbors = []

    for move_name, row, col in moves:
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            tile_index = row * GRID_SIZE + col
            neighbors.append((move_name, move_tile(state, tile_index)))

    return neighbors


def shuffle_state(state=GOAL_STATE, moves=30):
    """
    Shuffle by making valid moves from a solved state.
    This keeps the generated puzzle solvable.
    """
    current_state = state
    previous_state = None

    for _ in range(moves):
        neighbors = get_neighbors(current_state)

        if previous_state in neighbors and len(neighbors) > 1:
            neighbors.remove(previous_state)

        next_state = random.choice(neighbors)
        previous_state = current_state
        current_state = next_state

    return current_state
