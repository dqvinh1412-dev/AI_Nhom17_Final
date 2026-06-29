import time
from collections import deque
from algorithms.bfs import _result, reconstruct_path
from core.puzzle import get_neighbors_with_actions, shuffle_state

MAX_VISITED = 50000

def solve_no_goal(start_state, base_goal_state):
    """Sử dụng BFS tìm đường đến 1 trong 2 trạng thái Goal ngẫu nhiên."""
    start_time = time.perf_counter()

    # Sinh 2 trạng thái Goal hợp lệ
    target_goals = [shuffle_state(base_goal_state, moves=10) for _ in range(2)]

    if start_state in target_goals:
        return _result([start_state], [], 0, start_time, True, "Start State đã trùng với 1 trong các Goals.")

    frontier = deque([start_state])
    explored = set()
    frontier_states = {start_state}
    parent = {start_state: None}
    action = {}

    while frontier:
        current_state = frontier.popleft()
        frontier_states.remove(current_state)
        explored.add(current_state)

        if len(explored) > MAX_VISITED:
            return _result([], [], len(explored), start_time, False, "BFS (No Goal) vượt giới hạn MAX_VISITED.")

        for move_name, child_state in get_neighbors_with_actions(current_state):
            if child_state not in explored and child_state not in frontier_states:
                parent[child_state] = current_state
                action[child_state] = move_name

                if child_state in target_goals:
                    path, moves = reconstruct_path(parent, action, start_state, child_state)
                    return _result(
                        path=path, moves=moves, visited=len(explored), start_time=start_time, success=True,
                        message="Đã tìm thấy 1 trong 2 trạng thái Goal ngẫu nhiên bằng BFS."
                    )

                frontier.append(child_state)
                frontier_states.add(child_state)

    return _result([], [], len(explored), start_time, False, "Không tìm thấy Goal nào.")