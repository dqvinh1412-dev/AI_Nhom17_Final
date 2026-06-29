import time
from algorithms.bfs import _result

def solve_forward_checking():
    """Giải CSP ma trận tăng dần bằng Forward Checking (FC)."""
    start_time = time.perf_counter()
    
    # Khởi tạo miền giá trị (Domain) cho 15 ô trống (từ 1 đến 15)
    domains = {i: list(range(1, 16)) for i in range(15)}
    assignment = [None] * 16
    assignment[15] = 0 # Ô cuối cùng mặc định là 0
    visited_nodes = [0]
    
    def forward_check(var_index):
        if var_index == 15:
            return True
            
        # Lưu lại trạng thái domain hiện tại để khôi phục nếu cần quay lui
        original_domains = {k: list(v) for k, v in domains.items()}
        
        for val in domains[var_index]:
            visited_nodes[0] += 1
            assignment[var_index] = val
            
            is_valid = True
            # --- KIỂM TRA TỚI (FORWARD CHECKING) ---
            for future_var in range(var_index + 1, 15):
                # Ràng buộc 1: Alldiff (Không trùng lặp)
                if val in domains[future_var]:
                    domains[future_var].remove(val)
                # Ràng buộc 2: Tăng dần
                domains[future_var] = [v for v in domains[future_var] if v > val]
                
                # Cắt tỉa: Nếu bất kỳ ô tương lai nào hết lựa chọn -> Nhánh này vô nghiệm
                if not domains[future_var]:
                    is_valid = False
                    break
            
            if is_valid:
                if forward_check(var_index + 1):
                    return True
                    
            # Quay lui: Khôi phục lại domain gốc
            for k in domains:
                domains[k] = list(original_domains[k])
                
        assignment[var_index] = None
        return False

    success = forward_check(0)
    
    return _result(
        path=[tuple(assignment)] if success else [],
        moves=["Điền số"] * 15 if success else [],
        visited=visited_nodes[0],
        start_time=start_time,
        success=success,
        message="Hoàn thành CSP bằng Forward Checking." if success else "CSP thất bại."
    )