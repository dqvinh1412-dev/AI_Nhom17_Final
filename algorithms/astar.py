import time
import heapq
from algorithms.bfs import _result, reconstruct_path
from core.puzzle import get_neighbors_with_actions

MAX_VISITED = 50000

def get_manhattan_distance(state, goal_state):
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

def solve_astar(start_state, goal_state):
    """Giải 15-puzzle bằng thuật toán A* Search."""
    start_time = time.perf_counter()

    if start_state == goal_state:
        return _result([start_state], [], 0, start_time, True, "Start State đã là Goal State.")

    # Priority queue lưu trữ: (f_cost, counter, state)
    counter = 0
    frontier = [(get_manhattan_distance(start_state, goal_state), counter, start_state)]
    
    # Dictionary lưu g_cost (chi phí thực tế từ Start đến State hiện tại)
    g_costs = {start_state: 0}
    explored = set()
    parent = {start_state: None}
    action = {}

    while frontier:
        _, _, current_state = heapq.heappop(frontier)

        if current_state == goal_state:
            path, moves = reconstruct_path(parent, action, start_state, goal_state)
            return _result(path, moves, len(explored), start_time, True, "Tìm thấy lời giải tối ưu bằng A*.")

        explored.add(current_state)

        if len(explored) > MAX_VISITED:
            return _result([], [], len(explored), start_time, False, "A* vượt quá giới hạn trạng thái duyệt.")

        for move_name, child_state in get_neighbors_with_actions(current_state):
            new_g_cost = g_costs[current_state] + 1

            if child_state not in g_costs or new_g_cost < g_costs[child_state]:
                g_costs[child_state] = new_g_cost
                f_cost = new_g_cost + get_manhattan_distance(child_state, goal_state)
                
                parent[child_state] = current_state
                action[child_state] = move_name
                
                counter += 1
                heapq.heappush(frontier, (f_cost, counter, child_state))

    return _result([], [], len(explored), start_time, False, "A* không tìm thấy lời giải.")