import time
from algorithms.bfs import _result

def is_consistent(var_index, value, assignment):
    """Kiểm tra giá trị 'value' gán vào ô 'var_index' có thỏa mãn ràng buộc không."""
    # Ràng buộc Alldiff
    if value in assignment:
        return False
    # Ràng buộc tăng dần
    if var_index > 0 and assignment[var_index - 1] is not None:
        if value <= assignment[var_index - 1]:
            return False
    return True

def solve_backtracking_csp():
    """Giải bài toán điền số bằng Backtracking CSP."""
    start_time = time.perf_counter()
    
    # 16 biến (ô trống). Ô cuối (index 15) mặc định là 0 (Blank).
    assignment = [None] * 16
    assignment[15] = 0 
    visited_nodes = [0]
    
    def backtrack(var_index):
        if var_index == 15: # Đã gán xong 15 biến
            return True
            
        # Miền giá trị (Domain) từ 1 đến 15
        for value in range(1, 16):
            visited_nodes[0] += 1
            if is_consistent(var_index, value, assignment):
                assignment[var_index] = value 
                
                if backtrack(var_index + 1):
                    return True
                    
                assignment[var_index] = None # Quay lui
        return False

    success = backtrack(0)
    
    return _result(
        path=[tuple(assignment)] if success else [],
        moves=["Điền số"] * 15 if success else [],
        visited=visited_nodes[0],
        start_time=start_time,
        success=success,
        message="Hoàn thành CSP bằng Backtracking." if success else "CSP thất bại."
    )