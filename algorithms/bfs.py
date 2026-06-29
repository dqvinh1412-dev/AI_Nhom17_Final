import time
from collections import deque

from core.puzzle import get_neighbors_with_actions


MAX_VISITED = 50000


def solve_bfs(start_state, goal_state):
    """Solve 15-puzzle with BFS2 - Early Goal Test."""
    start_time = time.perf_counter()

    if start_state == goal_state:
        return {
            "path": [start_state],
            "moves": [],
            "steps": 0,
            "visited": 0,
            "time": round(time.perf_counter() - start_time, 4),
            "success": True,
            "message": "Start State đã là Goal State.",
        }

    # frontier is a FIFO queue: states waiting to be expanded.
    frontier = deque([start_state])

    # explored stores states that have already been expanded.
    explored = set()

    # frontier_states helps avoid putting duplicate states into the queue.
    frontier_states = {start_state}

    # parent and action are used later to reconstruct the final solution path.
    parent = {start_state: None}
    action = {}

    while frontier:
        current_state = frontier.popleft()
        frontier_states.remove(current_state)
        explored.add(current_state)

        if len(explored) > MAX_VISITED:
            return _result(
                path=[],
                moves=[],
                visited=len(explored),
                start_time=start_time,
                success=False,
                message="BFS đã vượt quá giới hạn trạng thái duyệt. Hãy dùng trạng thái gần Goal hơn.",
            )

        for move_name, child_state in get_neighbors_with_actions(current_state):
            if child_state in explored or child_state in frontier_states:
                continue

            parent[child_state] = current_state
            action[child_state] = move_name

            # BFS2 - Early Goal Test: check the goal as soon as a child is generated.
            if child_state == goal_state:
                path, moves = reconstruct_path(parent, action, start_state, goal_state)
                return _result(
                    path=path,
                    moves=moves,
                    visited=len(explored),
                    start_time=start_time,
                    success=True,
                    message="Tìm thấy lời giải bằng BFS2 - Early Goal Test.",
                )

            frontier.append(child_state)
            frontier_states.add(child_state)

    return _result(
        path=[],
        moves=[],
        visited=len(explored),
        start_time=start_time,
        success=False,
        message="BFS không tìm thấy lời giải.",
    )


def reconstruct_path(parent, action, start_state, goal_state):
    """Rebuild the path by going from goal back to start, then reversing it."""
    path = []
    moves = []
    state = goal_state

    while state is not None:
        path.append(state)
        if state != start_state:
            moves.append(action[state])
        state = parent[state]

    path.reverse()
    moves.reverse()
    return path, moves


def format_state(state):
    """Format a tuple state as a readable 4x4 board for the Solution Log."""
    rows = []
    for row in range(4):
        values = state[row * 4 : (row + 1) * 4]
        rows.append(" ".join(f"{value:>2}" if value != 0 else " 0" for value in values))
    return "\n".join(rows)


def _result(path, moves, visited, start_time, success, message):
    return {
        "path": path,
        "moves": moves,
        "steps": max(0, len(path) - 1),
        "visited": visited,
        "time": round(time.perf_counter() - start_time, 4),
        "success": success,
        "message": message,
    }
