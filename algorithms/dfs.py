import time
from algorithms.bfs import _result, reconstruct_path
from core.puzzle import get_neighbors_with_actions

MAX_VISITED = 50000

def solve_dfs(start_state, goal_state):
    """Solve 15-puzzle with DFS - Early Goal Test."""
    start_time = time.perf_counter()

    if start_state == goal_state:
        return _result([start_state], [], 0, start_time, True, "Start State đã là Goal State.")

    # DFS dùng Stack (LIFO)
    frontier = [start_state]
    explored = set()
    frontier_states = {start_state}
    
    parent = {start_state: None}
    action = {}

    while frontier:
        current_state = frontier.pop()
        frontier_states.remove(current_state)
        explored.add(current_state)

        if len(explored) > MAX_VISITED:
            return _result(
                path=[], moves=[], visited=len(explored), start_time=start_time, success=False,
                message="DFS đã vượt quá giới hạn trạng thái duyệt. Hãy thử load sample gần Goal."
            )

        for move_name, child_state in get_neighbors_with_actions(current_state):
            if child_state not in explored and child_state not in frontier_states:
                parent[child_state] = current_state
                action[child_state] = move_name

                # Early Goal Test
                if child_state == goal_state:
                    path, moves = reconstruct_path(parent, action, start_state, goal_state)
                    return _result(
                        path=path, moves=moves, visited=len(explored), start_time=start_time, success=True,
                        message="Tìm thấy lời giải bằng DFS - Early Goal Test."
                    )

                frontier.append(child_state)
                frontier_states.add(child_state)

    return _result([], [], len(explored), start_time, False, "DFS không tìm thấy lời giải.")