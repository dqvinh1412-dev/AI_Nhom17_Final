import time
import heapq
from algorithms.bfs import _result, reconstruct_path
from core.puzzle import get_neighbors_with_actions

MAX_VISITED = 50000

def manhattan_distance(state, goal_state):
    """Tính tổng khoảng cách Manhattan từ các ô hiện tại đến vị trí đích của chúng."""
    dist = 0
    for i in range(16):
        val = state[i]
        if val != 0:
            goal_idx = goal_state.index(val)
            curr_r, curr_c = divmod(i, 4)
            goal_r, goal_c = divmod(goal_idx, 4)
            dist += abs(curr_r - goal_r) + abs(curr_c - goal_c)
    return dist

def solve_greedy(start_state, goal_state):
    """Solve 15-puzzle using Greedy Search (chỉ phụ thuộc heuristic h(n))."""
    start_time = time.perf_counter()

    if start_state == goal_state:
        return _result([start_state], [], 0, start_time, True, "Start State đã là Goal State.")

    counter = 0  # Tie-breaker cho Priority Queue
    # Hàng đợi ưu tiên chứa tuple (h_cost, counter, state)
    frontier = [(manhattan_distance(start_state, goal_state), counter, start_state)]
    explored = set()
    
    parent = {start_state: None}
    action = {}

    while frontier:
        _, _, current_state = heapq.heappop(frontier)
        
        if current_state == goal_state:
            path, moves = reconstruct_path(parent, action, start_state, goal_state)
            return _result(path, moves, len(explored), start_time, True, "Tìm thấy lời giải bằng Greedy Search.")

        explored.add(current_state)

        if len(explored) > MAX_VISITED:
            return _result([], [], len(explored), start_time, False, "Greedy Search vượt quá giới hạn duyệt.")

        for move_name, child_state in get_neighbors_with_actions(current_state):
            if child_state not in explored:
                parent[child_state] = current_state
                action[child_state] = move_name
                
                counter += 1
                h_cost = manhattan_distance(child_state, goal_state)
                heapq.heappush(frontier, (h_cost, counter, child_state))

    return _result([], [], len(explored), start_time, False, "Greedy không tìm thấy lời giải.")