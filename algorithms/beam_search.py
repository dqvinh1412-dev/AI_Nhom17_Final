import time
from algorithms.bfs import _result, reconstruct_path
from algorithms.greedy import manhattan_distance
from core.puzzle import get_neighbors_with_actions

MAX_VISITED = 50000

def solve_beam_search(start_state, goal_state, k=2):
    """Solve 15-puzzle using Local Beam Search với k=2."""
    start_time = time.perf_counter()

    if start_state == goal_state:
        return _result([start_state], [], 0, start_time, True, "Start State đã là Goal State.")

    # Beam giữ k trạng thái tốt nhất ở mỗi bước
    beam = [start_state]
    explored = set()
    
    parent = {start_state: None}
    action = {}

    while beam:
        next_states = []

        for current_state in beam:
            if current_state == goal_state:
                path, moves = reconstruct_path(parent, action, start_state, goal_state)
                return _result(path, moves, len(explored), start_time, True, "Tìm thấy lời giải bằng Local Beam Search.")

            explored.add(current_state)

            if len(explored) > MAX_VISITED:
                return _result([], [], len(explored), start_time, False, "Local Beam Search vượt quá giới hạn duyệt.")

            for move_name, child_state in get_neighbors_with_actions(current_state):
                if child_state not in explored:
                    parent[child_state] = current_state
                    action[child_state] = move_name
                    
                    h_cost = manhattan_distance(child_state, goal_state)
                    next_states.append((h_cost, child_state))

        if not next_states:
            break

        # Sắp xếp theo Heuristic tăng dần và chỉ lấy k trạng thái tốt nhất
        next_states.sort(key=lambda x: x[0])
        beam = [state for cost, state in next_states[:k]]

    return _result([], [], len(explored), start_time, False, "Local Beam Search bị mắc kẹt (Không tìm thấy).")