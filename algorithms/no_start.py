import time
from algorithms.bfs import _result
from algorithms.greedy import solve_greedy
from core.puzzle import shuffle_state

def solve_no_start(goal_state):
    """Tạo 2 Start State ngẫu nhiên, chạy Greedy cho cả 2 và lấy kết quả tốt hơn."""
    start_time = time.perf_counter()
    
    # Sinh 2 start ngẫu nhiên (số bước tráo từ Goal nhỏ để Greedy có thể giải nhanh)
    start_1 = shuffle_state(goal_state, moves=12)
    start_2 = shuffle_state(goal_state, moves=15)
    
    res_1 = solve_greedy(start_1, goal_state)
    res_2 = solve_greedy(start_2, goal_state)
    
    best_res = res_1
    best_start = start_1
    if res_1["success"] and res_2["success"]:
        if res_1["steps"] <= res_2["steps"]:
            best_res = res_1
            best_start = start_1
        else:
            best_res = res_2
            best_start = start_2
    elif res_2["success"]:
        best_res = res_2
        best_start = start_2
        
    best_res["message"] = f"No Start (Đã thử 2 Starts): {best_res['message']}"
    best_res["time"] = round(time.perf_counter() - start_time, 4)
    
    best_res["start_state"] = best_start
    best_res["generated_start"] = best_start
    best_res["goal_state"] = goal_state
    best_res["tried_starts"] = [start_1, start_2]
    
    return best_res
