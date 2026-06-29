import time
from algorithms.bfs import _result, reconstruct_path
from core.puzzle import get_neighbors_with_actions
from algorithms.astar import get_manhattan_distance

MAX_VISITED = 50000

def solve_hill_climbing(start_state, goal_state):
    """Giải 15-puzzle bằng Simple Hill Climbing (Steepest Ascent)."""
    start_time = time.perf_counter()

    if start_state == goal_state:
        return _result([start_state], [], 0, start_time, True, "Start State đã là Goal State.")

    current_state = start_state
    parent = {start_state: None}
    action = {}
    explored = set()

    while True:
        explored.add(current_state)
        current_h = get_manhattan_distance(current_state, goal_state)

        if current_state == goal_state:
            path, moves = reconstruct_path(parent, action, start_state, goal_state)
            return _result(path, moves, len(explored), start_time, True, "Hill Climbing tìm thấy lời giải thành công.")

        if len(explored) > MAX_VISITED:
            return _result([], [], len(explored), start_time, False, "Hill Climbing vượt quá giới hạn duyệt.")

        # Tìm neighbor tốt nhất
        neighbors = get_neighbors_with_actions(current_state)
        best_neighbor = None
        best_move = None
        best_h = float('inf')

        for move_name, child_state in neighbors:
            if child_state not in explored:
                h = get_manhattan_distance(child_state, goal_state)
                if h < best_h:
                    best_h = h
                    best_neighbor = child_state
                    best_move = move_name

        # Kiểm tra kẹt ở Local Optima: Nếu neighbor tốt nhất vẫn tệ hơn/bằng hiện tại thì dừng
        if best_neighbor is None or best_h >= current_h:
            return _result([], [], len(explored), start_time, False, "Hill Climbing bị mắc kẹt tại Local Optima.")

        parent[best_neighbor] = current_state
        action[best_neighbor] = best_move
        current_state = best_neighbor