import time
import math
import tkinter as tk
from tkinter import ttk, messagebox

from core.puzzle import GOAL_STATE, can_move, move_tile, shuffle_state
from algorithms.bfs import solve_bfs
from algorithms.dfs import solve_dfs
from algorithms.greedy import solve_greedy
from algorithms.beam_search import solve_beam_search
from algorithms.astar import solve_astar
from algorithms.hill_climbing import solve_hill_climbing
from algorithms.no_start import solve_no_start
from algorithms.no_goal import solve_no_goal
from algorithms.tic_tac_toe import minimax, alpha_beta, check_winner

# --- UI Theme Colors ---
BG_COLOR = "#050816"
PANEL_COLOR = "#070A13"
TILE_COLOR = "#111827"
TILE_ALT_COLOR = "#151A2E"
TEXT_COLOR = "#EAF2FF"
MUTED_TEXT = "#9CA3AF"
CYAN = "#00D4FF"
BUTTON_COLOR = "#111827"
BUTTON_HOVER = "#1F2937"
BUTTON_OUTLINE = "#263244"
TILE_OUTLINE = "#24344D"

TAB1_TEST_CASES = {
    "Test Case 1 - Dễ": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15),
    "Test Case 2 - Trung bình": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 13, 14, 15),
    "Test Case 3 - Khó vừa": (1, 2, 3, 4, 5, 6, 7, 8, 0, 10, 11, 12, 9, 13, 14, 15),
}

def format_state_grid(state):
    """Hàm bổ trợ: Chuyển đổi tuple 16 số thành chuỗi ma trận 4x4 dễ nhìn trên Log."""
    if not state: return ""
    res = []
    for i in range(4):
        row = state[i*4:(i+1)*4]
        res.append(" ".join(f"{x:2}" if x != 0 else " 0" for x in row))
    return "\n".join(res)

class CanvasButton:
    def __init__(self, parent, text, command, width=128, height=38):
        self.command = command
        parent_bg = parent.cget("bg") if hasattr(parent, "cget") else BG_COLOR
        self.canvas = tk.Canvas(parent, width=width, height=height, bg=parent_bg, highlightthickness=0, bd=0)
        self.rect = rounded_rectangle(self.canvas, 2, 2, width - 2, height - 2, radius=12, fill=BUTTON_COLOR, outline=BUTTON_OUTLINE, width=2)
        self.canvas.create_text(width / 2, height / 2, text=text, fill=TEXT_COLOR, font=("Segoe UI", 9, "bold"))
        self.canvas.bind("<Enter>", lambda e: [self.canvas.itemconfig(self.rect, fill=BUTTON_HOVER), self.canvas.config(cursor="hand2")])
        self.canvas.bind("<Leave>", lambda e: [self.canvas.itemconfig(self.rect, fill=BUTTON_COLOR), self.canvas.config(cursor="")])
        self.canvas.bind("<Button-1>", lambda e: self.command())

    def grid(self, **kwargs): self.canvas.grid(**kwargs)
    def pack(self, **kwargs): self.canvas.pack(**kwargs)

def rounded_rectangle(canvas, x1, y1, x2, y2, radius=18, **kwargs):
    points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("15-Puzzle AI Solver Pro")
        self.geometry("1350x850")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)

        self.tab1_state = GOAL_STATE
        self.tab2_state = GOAL_STATE
        self.tab2_start_state = None
        self.tab2_goal_state = GOAL_STATE
        self.tab2_goal_unknown = False
        self.solution_path, self.solution_moves, self.solution_step_index, self.moves = [], [], 0, 0
        self.solution_owner = None
        self.csp_animation_running = False
        self.csp_animation_token = 0
        self.caro_board, self.caro_status = [0] * 9, "Lượt của bạn (X)"

        self.tile_size, self.gap = 86, 26
        self.board_size = self.tile_size * 4 + self.gap * 3
        self.board_x, self.board_y = 420, 112

        self._create_styles()
        self._create_widgets()
        
        self._refresh_tab1_view()
        self._refresh_tab2_view()
        self.update_start_panel(None)
        self.update_goal_panel(GOAL_STATE)
        self._draw_tab3_grid([None]*16)
        self._draw_caro_board()

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Modern.TCombobox", fieldbackground=TILE_COLOR, background=TILE_COLOR, foreground=TEXT_COLOR, arrowcolor=CYAN, bordercolor=BUTTON_OUTLINE, padding=8)
        style.map("Modern.TCombobox", fieldbackground=[("readonly", TILE_COLOR)], foreground=[("readonly", TEXT_COLOR)])
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_COLOR, foreground=MUTED_TEXT, padding=[25, 8], font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", BG_COLOR)], foreground=[("selected", CYAN)])

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab1 = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab2 = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab3 = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab4 = tk.Frame(self.notebook, bg=BG_COLOR)

        self.notebook.add(self.tab1, text="1. TÌM KIẾM CƠ BẢN")
        self.notebook.add(self.tab2, text="2. MÔI TRƯỜNG PHỨC TẠP")
        self.notebook.add(self.tab3, text="3. RÀNG BUỘC (CSP)")
        self.notebook.add(self.tab4, text="4. ĐỐI KHÁNG (CARO)")

        self._build_tab1()
        self._build_tab2()
        self._build_tab3()
        self._build_tab4()

    # =========================================================================
    # TAB 1: TÌM KIẾM CƠ BẢN
    # =========================================================================
    def _build_tab1(self):
        c = tk.Canvas(self.tab1, width=1350, height=800, bg=BG_COLOR, highlightthickness=0); c.pack(fill="both", expand=True)
        c.bind("<Button-1>", self._on_tab1_click)
        self.canvas_tab1 = c

        c.create_text(675, 42, text="15-Puzzle - Basic Algorithms", fill=CYAN, font=("Segoe UI", 24, "bold"))
        self.tab1_moves_text = c.create_text(470, 86, text="Moves: 0", fill=TEXT_COLOR, font=("Segoe UI", 14, "bold"))
        
        for coords in [(35, 116, 245, 324), (35, 348, 245, 556), (920, 30, 1320, 175), (920, 190, 1320, 345)]:
            rounded_rectangle(c, *coords, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)

        self.tab1_result_text = c.create_text(1120, 112, text="Sẵn sàng\n\nSố bước: 0\nĐã duyệt: 0", fill=TEXT_COLOR, font=("Segoe UI", 10), justify="left", width=350)
        
        self.tab1_algo_var = tk.StringVar(value="A* Search (Tối ưu)")
        self.tab1_combo = ttk.Combobox(self.tab1, textvariable=self.tab1_algo_var, values=["BFS (Mù)", "DFS (Mù)", "A* Search (Tối ưu)", "Greedy Search (Heuristic)", "Local Beam Search (k=2)", "Hill Climbing (Cục bộ)"], state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9))
        self.tab1_combo.place(x=945, y=218, width=220, height=34)

        self.tab1_test_case_var = tk.StringVar(value="Test Case 1 - Dễ")
        self.tab1_test_case_combo = ttk.Combobox(self.tab1, textvariable=self.tab1_test_case_var, values=list(TAB1_TEST_CASES.keys()), state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9))
        self.tab1_test_case_combo.place(x=945, y=263, width=220, height=34)

        test_case_frame = tk.Frame(self.tab1, bg=PANEL_COLOR)
        test_case_frame.place(x=945, y=306, width=220, height=34)
        CanvasButton(test_case_frame, "Load Test Case", self._tab1_load_test_case, width=160, height=30).pack()

        ctrl_frame = tk.Frame(self.tab1, bg=PANEL_COLOR)
        ctrl_frame.place(x=1175, y=218, width=130, height=126)
        CanvasButton(ctrl_frame, "Reset", self._tab1_reset, width=120, height=28).grid(row=0, column=0, pady=1)
        CanvasButton(ctrl_frame, "Random", self._tab1_random, width=120, height=28).grid(row=1, column=0, pady=1)
        CanvasButton(ctrl_frame, "Load Sample", self._tab1_load_sample, width=120, height=28).grid(row=2, column=0, pady=1)
        CanvasButton(ctrl_frame, "Solve", self._tab1_solve, width=120, height=28).grid(row=3, column=0, pady=1)

        sim_frame = tk.Frame(self.tab1, bg=BG_COLOR)
        sim_frame.place(x=420, y=592, width=470, height=44)
        CanvasButton(sim_frame, "Play Solution", self._play_solution, width=140).grid(row=0, column=0, padx=6)
        CanvasButton(sim_frame, "Next Step", self._next_step, width=140).grid(row=0, column=1, padx=6)
        CanvasButton(sim_frame, "Clear Log", self._clear_all_logs, width=140).grid(row=0, column=2, padx=6)

        # Log Tab 1
        log_frame = tk.Frame(self.tab1, bg=PANEL_COLOR)
        log_frame.place(x=920, y=360, width=400, height=380)
        self.tab1_log = tk.Text(log_frame, bg="#0B1020", fg=TEXT_COLOR, relief="flat", font=("Consolas", 9), state="disabled")
        self.tab1_log.pack(fill="both", expand=True)

    def _on_tab1_click(self, event):
        col, row = (event.x - self.board_x) // (self.tile_size + self.gap), (event.y - self.board_y) // (self.tile_size + self.gap)
        if 0 <= row < 4 and 0 <= col < 4:
            idx = row * 4 + col
            if can_move(self.tab1_state, idx):
                self.tab1_state = move_tile(self.tab1_state, idx)
                self.moves += 1; self.set_solution_path([], owner="tab1"); self._refresh_tab1_view()

    def _refresh_tab1_view(self):
        self.canvas_tab1.itemconfig(self.tab1_moves_text, text=f"Moves: {self.moves}")
        self._draw_puzzle_board(self.canvas_tab1, self.tab1_state, "t1_tile")
        self._draw_mini_board(self.canvas_tab1, self.tab1_state, 70, 170, "t1_p1")
        self._draw_mini_board(self.canvas_tab1, GOAL_STATE, 70, 402, "t1_p2")

    def _tab1_reset(self): self.tab1_state = GOAL_STATE; self.moves = 0; self.set_solution_path([], owner="tab1"); self._refresh_tab1_view(); self._append_log(self.tab1_log, "Đã Reset bàn cờ.")
    def _tab1_random(self): self.tab1_state = shuffle_state(GOAL_STATE, 12); self.moves = 0; self.set_solution_path([], owner="tab1"); self._refresh_tab1_view(); self._append_log(self.tab1_log, "Đã tạo Start State ngẫu nhiên.")
    def _tab1_load_sample(self): self.tab1_state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15); self.moves = 0; self.set_solution_path([], owner="tab1"); self._refresh_tab1_view(); self._append_log(self.tab1_log, "Đã load mẫu gần Goal.")

    def _tab1_load_test_case(self):
        selected_case = self.tab1_test_case_var.get()
        self.tab1_state = TAB1_TEST_CASES[selected_case]
        self.moves = 0
        self.set_solution_path([], owner="tab1")
        self._refresh_tab1_view()
        self._append_log(self.tab1_log, f"Đã load {selected_case}.")

    def _tab1_solve(self):
        algo = self.tab1_algo_var.get()
        self._append_log(self.tab1_log, f"\nĐang chạy thuật toán: {algo}...")
        self.update_idletasks()

        if "BFS" in algo: res = solve_bfs(self.tab1_state, GOAL_STATE)
        elif "DFS" in algo: res = solve_dfs(self.tab1_state, GOAL_STATE)
        elif "A*" in algo: res = solve_astar(self.tab1_state, GOAL_STATE)
        elif "Greedy" in algo: res = solve_greedy(self.tab1_state, GOAL_STATE)
        elif "Beam" in algo: res = solve_beam_search(self.tab1_state, GOAL_STATE)
        elif "Hill" in algo: res = solve_hill_climbing(self.tab1_state, GOAL_STATE)
        else: return

        self.set_solution_path(res["path"], res["moves"], owner="tab1")
        
        # In thông số tổng quát lên UI và Log
        msg = f"Trạng thái: {res['message']}\nSố bước: {res['steps']}\nĐã duyệt: {res['visited']}\nThời gian: {res['time']}s"
        self.canvas_tab1.itemconfig(self.tab1_result_text, text=msg)
        self._append_log(self.tab1_log, f"Kết quả: {res['message']} (Time: {res['time']}s)\n")

        # In CHI TIẾT TỪNG BƯỚC VÀ COST
        if res["path"]:
            self._append_log(self.tab1_log, "--- CHI TIẾT LỘ TRÌNH (STEPS & COST) ---")
            for i, state in enumerate(res["path"]):
                move = res["moves"][i-1] if i > 0 else "Trạng thái xuất phát"
                self._append_log(self.tab1_log, f"Bước {i} | {move} | Cost: {i}:\n{format_state_grid(state)}\n")

    # =========================================================================
    # TAB 2: MÔI TRƯỜNG PHỨC TẠP
    # =========================================================================
    def _build_tab2(self):
        c = tk.Canvas(self.tab2, width=1350, height=800, bg=BG_COLOR, highlightthickness=0); c.pack(fill="both", expand=True)
        self.canvas_tab2 = c

        c.create_text(675, 42, text="Môi trường Phức tạp (No Start / No Goal)", fill=CYAN, font=("Segoe UI", 24, "bold"))
        rounded_rectangle(c, 35, 116, 245, 324, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)
        rounded_rectangle(c, 35, 348, 245, 556, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)
        c.create_text(140, 142, text="Start State", fill=CYAN, font=("Segoe UI", 11, "bold"))
        c.create_text(140, 374, text="Goal State", fill=CYAN, font=("Segoe UI", 11, "bold"))
        rounded_rectangle(c, 920, 30, 1320, 175, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)
        rounded_rectangle(c, 920, 190, 1320, 345, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)
        
        self.tab2_result_text = c.create_text(1120, 112, text="Chờ kịch bản...", fill=TEXT_COLOR, font=("Segoe UI", 10), justify="left", width=350)
        self.tab2_algo_var = tk.StringVar(value="No Start (Greedy tìm kiếm)")
        self.tab2_combo = ttk.Combobox(self.tab2, textvariable=self.tab2_algo_var, values=["No Start (Greedy tìm kiếm)", "No Goal (BFS tìm kiếm)"], state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9))
        self.tab2_combo.place(x=945, y=235, width=220, height=34)
        self.tab2_combo.bind("<<ComboboxSelected>>", self._on_tab2_scenario_changed)

        ctrl_frame = tk.Frame(self.tab2, bg=PANEL_COLOR)
        ctrl_frame.place(x=1020, y=284, width=280, height=44)
        CanvasButton(ctrl_frame, "Chạy Kịch Bản", self._tab2_solve, width=150, height=34).pack()

        sim_frame = tk.Frame(self.tab2, bg=BG_COLOR)
        sim_frame.place(x=420, y=592, width=310, height=44)
        CanvasButton(sim_frame, "Play Solution", self._play_solution, width=140).grid(row=0, column=0, padx=6)
        CanvasButton(sim_frame, "Next Step", self._next_step, width=140).grid(row=0, column=1, padx=6)

        # Log Tab 2
        log_frame = tk.Frame(self.tab2, bg=PANEL_COLOR)
        log_frame.place(x=920, y=360, width=400, height=380)
        self.tab2_log = tk.Text(log_frame, bg="#0B1020", fg=TEXT_COLOR, relief="flat", font=("Consolas", 9), state="disabled")
        self.tab2_log.pack(fill="both", expand=True)

    def _refresh_tab2_view(self): self._draw_puzzle_board(self.canvas_tab2, self.tab2_state, "t2_tile")

    def _on_tab2_scenario_changed(self, _event=None):
        if "No Goal" in self.tab2_algo_var.get():
            self.update_start_panel(self.tab2_state)
            self.update_goal_panel(None, unknown=True)
        else:
            self.update_start_panel(None)
            self.update_goal_panel(GOAL_STATE)

    def _tab2_solve(self):
        kich_ban = self.tab2_algo_var.get()
        self.set_solution_path([], owner="tab2")
        self._append_log(self.tab2_log, f"\nĐang chạy kịch bản: {kich_ban}...")
        self.update_idletasks()

        if "No Start" in kich_ban:
            self.update_start_panel(None)
            self.update_goal_panel(GOAL_STATE)
            res = solve_no_start(GOAL_STATE)
            path_states, path_key = self._result_state_sequence(res, ("path", "solution_path"))
            start_st = self._result_state(res, ("start_state", "generated_start")) or (path_states[0] if path_states else None)
            goal_st = self._result_state(res, ("goal_state",)) or GOAL_STATE

            self._append_log(self.tab2_log, "--- THÔNG TIN KHỞI TẠO ---")
            self._log_tried_states(res, ("tried_starts", "starts"), "Start đã thử")
            if start_st:
                self.update_start_panel(start_st)
                self._append_log(self.tab2_log, f"[Start State Sinh/Chọn]:\n{format_state_grid(start_st)}\n")
            else:
                self._append_log(self.tab2_log, "[Start State]: Chưa xác định từ kết quả thuật toán.")
            self.update_goal_panel(goal_st)
            self._append_log(self.tab2_log, f"[Goal State Mặc Định]:\n{format_state_grid(goal_st)}\n")
        else:
            start_st = self.tab2_state
            self.update_start_panel(start_st)
            self.update_goal_panel(None, unknown=True)
            res = solve_no_goal(start_st, GOAL_STATE)
            path_states, path_key = self._result_state_sequence(res, ("path", "solution_path"))
            start_st = self._result_state(res, ("start_state",)) or start_st

            self._append_log(self.tab2_log, "--- THÔNG TIN KHỞI TẠO ---")
            self.update_start_panel(start_st)
            self._append_log(self.tab2_log, f"[Start State Đầu Vào]:\n{format_state_grid(start_st)}\n")
            self._append_log(self.tab2_log, "[Goal State]: No Goal / Unknown\n")

        demo_states = path_states
        demo_key = path_key
        if not demo_states:
            demo_states, demo_key = self._result_state_sequence(res, ("states", "visited_states"))

        moves = res.get("moves", []) if isinstance(res, dict) else []
        if demo_states:
            self.set_solution_path(demo_states, moves, owner="tab2")
            self.update_main_board(demo_states[0])
            self._append_log(self.tab2_log, f"Đã nạp dữ liệu mô phỏng từ result['{demo_key}'] ({len(demo_states)} trạng thái).")
        else:
            fallback_state = start_st if "No Goal" in kich_ban else (start_st or GOAL_STATE)
            self.update_main_board(fallback_state)
            self._append_log(self.tab2_log, "Thuật toán không trả về path để mô phỏng.")

        msg = f"Kết quả: {res.get('message', 'Không có message')}\nĐộ sâu: {res.get('steps', 0)}\nĐã duyệt: {res.get('visited', 0)}\nThời gian: {res.get('time', 0)}s"
        self.canvas_tab2.itemconfig(self.tab2_result_text, text=msg)
        
        # IN CHI TIẾT TỪNG BƯỚC
        if demo_states:
            self._append_log(self.tab2_log, "--- CHI TIẾT LỘ TRÌNH TÌM KIẾM ---")
            for i, state in enumerate(demo_states):
                move = moves[i-1] if i > 0 and i-1 < len(moves) else "Start"
                self._append_log(self.tab2_log, f"Bước {i} ({move}):\n{format_state_grid(state)}\n")

    # =========================================================================
    # TAB 3: THỎA MÃN RÀNG BUỘC (CSP) - TÍCH HỢP TRACER THEO DÕI DOMAIN
    # =========================================================================
    def _build_tab3(self):
        c = tk.Canvas(self.tab3, width=1350, height=800, bg=BG_COLOR, highlightthickness=0); c.pack(fill="both", expand=True)
        self.canvas_tab3 = c

        c.create_text(675, 42, text="Bài toán Thỏa mãn Ràng buộc (CSP)", fill=CYAN, font=("Segoe UI", 24, "bold"))
        rounded_rectangle(c, 920, 190, 1320, 345, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)

        self.tab3_algo_var = tk.StringVar(value="Forward Checking (FC)")
        self.tab3_combo = ttk.Combobox(self.tab3, textvariable=self.tab3_algo_var, values=["Backtracking (CSP)", "Forward Checking (FC)"], state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9))
        self.tab3_combo.place(x=945, y=235, width=220, height=34)

        ctrl_frame = tk.Frame(self.tab3, bg=PANEL_COLOR)
        ctrl_frame.place(x=950, y=284, width=340, height=44)
        CanvasButton(ctrl_frame, "Giải CSP", self._tab3_solve, width=130, height=34).grid(row=0, column=0, padx=5)
        CanvasButton(ctrl_frame, "Xóa Bàn Cờ", self._tab3_clear_board, width=130, height=34).grid(row=0, column=1, padx=5)

        # Log Tab 3
        log_frame = tk.Frame(self.tab3, bg=PANEL_COLOR)
        log_frame.place(x=920, y=360, width=400, height=380)
        self.tab3_log = tk.Text(log_frame, bg="#0B1020", fg=TEXT_COLOR, relief="flat", font=("Consolas", 9), state="disabled")
        self.tab3_log.pack(fill="both", expand=True)

    def _draw_tab3_grid(self, assignment, highlight_index=None, highlight_type=None):
        self.canvas_tab3.delete("csp_tile")
        rounded_rectangle(self.canvas_tab3, self.board_x - 18, self.board_y - 18, self.board_x + self.board_size + 18, self.board_y + self.board_size + 18, radius=28, fill=PANEL_COLOR, outline="#101827", width=2, tags="csp_tile")
        for idx in range(16):
            row, col = divmod(idx, 4)
            x, y = self.board_x + col * (self.tile_size + self.gap), self.board_y + row * (self.tile_size + self.gap)
            val = assignment[idx]
            fill_color, txt = (TILE_COLOR, str(val)) if (val is not None and val != 0) else (BG_COLOR, "")
            outline_color = TILE_OUTLINE
            text_color = CYAN
            if idx == highlight_index:
                if highlight_type in ("try", "assign", "domain", "success"):
                    fill_color, outline_color, text_color = "#083344", CYAN, TEXT_COLOR
                elif highlight_type in ("backtrack", "fail"):
                    fill_color, outline_color, text_color = "#3B1119", "#FF4A4A", TEXT_COLOR
            rounded_rectangle(self.canvas_tab3, x, y, x + self.tile_size, y + self.tile_size, radius=18, fill=fill_color, outline=outline_color, width=2, tags="csp_tile")
            if txt: self.canvas_tab3.create_text(x + self.tile_size/2, y + self.tile_size/2, text=txt, fill=text_color, font=("Segoe UI", 24, "bold"), tags="csp_tile")

    def _tab3_clear_board(self):
        self.csp_animation_token += 1
        self.csp_animation_running = False
        self._draw_tab3_grid([None]*16)
        self._append_log(self.tab3_log, "\nĐã xóa bàn cờ CSP.")

    def _csp_assignment_snapshot(self, assignment, override_index=None, override_value=None):
        snapshot = list(assignment)
        if override_index is not None:
            snapshot[override_index] = override_value
        return tuple(snapshot)

    def _add_csp_trace(self, steps, assignment, message, step_type, highlight_index=None, override_value=None):
        steps.append({
            "assignment": self._csp_assignment_snapshot(assignment, highlight_index, override_value),
            "message": message,
            "type": step_type,
            "highlight_index": highlight_index,
        })

    def _animate_csp_steps(self, steps, index=0, token=None):
        if token != self.csp_animation_token:
            return
        if index >= len(steps):
            self.csp_animation_running = False
            return
        step = steps[index]
        self._draw_tab3_grid(step["assignment"], step.get("highlight_index"), step.get("type"))
        self._append_log(self.tab3_log, step["message"])
        self.after(300, lambda: self._animate_csp_steps(steps, index + 1, token))

    def _tab3_solve(self):
        """Hàm tích hợp Tracer nội bộ để Log trực tiếp Miền Giá Trị cho UI."""
        if self.csp_animation_running:
            self._append_log(self.tab3_log, "CSP đang mô phỏng, vui lòng chờ animation hiện tại kết thúc.")
            return

        algo = self.tab3_algo_var.get()
        self._append_log(self.tab3_log, f"\nĐang giải CSP bằng: {algo}...")
        self.update_idletasks()
        
        start_t = time.perf_counter()
        visited = [0]
        assignment = [None] * 16; assignment[15] = 0
        trace_steps = []
        success = False

        if "Backtracking" in algo:
            def bt(var_idx):
                if var_idx == 15: return True
                for val in range(1, 16):
                    visited[0] += 1
                    is_valid = (val not in assignment)
                    if is_valid and var_idx > 0 and assignment[var_idx-1] is not None:
                        if val <= assignment[var_idx-1]: is_valid = False
                        
                    self._add_csp_trace(trace_steps, assignment, f"-> Thử gán Ô {var_idx} = {val} | Hợp lệ: {is_valid}", "try", var_idx, val)
                    if is_valid:
                        assignment[var_idx] = val
                        self._add_csp_trace(trace_steps, assignment, f"   Gán Ô {var_idx} = {val} thành công", "assign", var_idx)
                        if bt(var_idx + 1): return True
                        assignment[var_idx] = None
                        self._add_csp_trace(trace_steps, assignment, f"   [!] Bế tắc, Quay lui (Backtrack) gỡ bỏ Ô {var_idx}", "backtrack", var_idx)
                return False
            success = bt(0)
            
        else: # Forward Checking (FC)
            domains = {i: list(range(1, 16)) for i in range(15)}
            def fc(var_idx):
                if var_idx == 15: return True
                orig_domains = {k: list(v) for k, v in domains.items()}
                
                for val in domains[var_idx]:
                    visited[0] += 1
                    assignment[var_idx] = val
                    self._add_csp_trace(trace_steps, assignment, f"-> Gán Ô {var_idx} = {val}", "assign", var_idx)
                    
                    is_valid = True
                    for fut in range(var_idx + 1, 15):
                        if val in domains[fut]: domains[fut].remove(val)
                        domains[fut] = [v for v in domains[fut] if v > val]
                        if not domains[fut]: is_valid = False
                        
                    # LOG DOMAIN (Chỉ in 3 ô tiếp theo cho gọn Log)
                    dom_strs = [f"Ô_{i}:{domains[i]}" for i in range(var_idx+1, min(var_idx+4, 15))]
                    self._add_csp_trace(trace_steps, assignment, f"   Forward Checking: cập nhật miền giá trị | {', '.join(dom_strs)}", "domain", var_idx)
                    
                    if is_valid:
                        if fc(var_idx + 1): return True
                    else:
                        self._add_csp_trace(trace_steps, assignment, f"   [!] Hết miền giá trị, nhánh này vô nghiệm, Quay lui!", "fail", var_idx)
                        
                    for k in domains: domains[k] = list(orig_domains[k])
                    assignment[var_idx] = None
                    self._add_csp_trace(trace_steps, assignment, f"   Quay lui tại Ô {var_idx}", "backtrack", var_idx)
                return False
            success = fc(0)

        t = round(time.perf_counter() - start_t, 4)
        if success:
            finish_msg = "Hoàn thành Backtracking" if "Backtracking" in algo else "Hoàn thành Forward Checking"
            self._add_csp_trace(trace_steps, assignment, f"\n{finish_msg}\nThành công! Số nút duyệt: {visited[0]}. Thời gian: {t}s", "success")
        else:
            self._add_csp_trace(trace_steps, assignment, "\nThất bại, không tìm được cấu hình thỏa mãn ràng buộc.", "fail")

        self.csp_animation_running = True
        self.csp_animation_token += 1
        self._animate_csp_steps(trace_steps, token=self.csp_animation_token)

    # =========================================================================
    # TAB 4: TÌM KIẾM ĐỐI KHÁNG (CARO)
    # =========================================================================
    def _build_tab4(self):
        c = tk.Canvas(self.tab4, width=1350, height=800, bg=BG_COLOR, highlightthickness=0); c.pack(fill="both", expand=True)
        c.bind("<Button-1>", self._on_caro_click)
        self.canvas_tab4 = c

        c.create_text(675, 42, text="Tìm kiếm Đối kháng (Caro 3x3)", fill=CYAN, font=("Segoe UI", 24, "bold"))
        self.caro_status_text = c.create_text(675, 90, text=self.caro_status, fill=TEXT_COLOR, font=("Segoe UI", 14, "bold"))
        rounded_rectangle(c, 940, 190, 1300, 345, radius=18, fill=PANEL_COLOR, outline="#101827", width=2)

        self.tab4_algo_var = tk.StringVar(value="Alpha-Beta Pruning")
        self.tab4_combo = ttk.Combobox(self.tab4, textvariable=self.tab4_algo_var, values=["Minimax (Thuần túy)", "Alpha-Beta Pruning"], state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9))
        self.tab4_combo.place(x=965, y=245, width=180, height=34)
        
        ctrl_frame = tk.Frame(self.tab4, bg=PANEL_COLOR)
        ctrl_frame.place(x=965, y=295, width=170, height=44)
        CanvasButton(ctrl_frame, "Chơi ván mới", self._reset_caro, width=150, height=34).pack()

        # Log Tab 4
        log_frame = tk.Frame(self.tab4, bg=PANEL_COLOR)
        log_frame.place(x=920, y=360, width=400, height=380)
        self.tab4_log = tk.Text(log_frame, bg="#0B1020", fg=TEXT_COLOR, relief="flat", font=("Consolas", 9), state="disabled")
        self.tab4_log.pack(fill="both", expand=True)

    def _draw_caro_board(self):
        self.canvas_tab4.delete("caro")
        self.canvas_tab4.itemconfig(self.caro_status_text, text=self.caro_status)
        cx, cy, c_size, c_gap = 480, 150, 110, 15
        rounded_rectangle(self.canvas_tab4, cx - 15, cy - 15, cx + c_size*3 + c_gap*2 + 15, cy + c_size*3 + c_gap*2 + 15, radius=20, fill=PANEL_COLOR, outline="#101827", width=2, tags="caro")

        for idx in range(9):
            row, col = divmod(idx, 3)
            x, y = cx + col * (c_size + c_gap), cy + row * (c_size + c_gap)
            rounded_rectangle(self.canvas_tab4, x, y, x + c_size, y + c_size, radius=12, fill=TILE_COLOR, outline=TILE_OUTLINE, width=2, tags="caro")
            val = self.caro_board[idx]
            txt, color = ("", TEXT_COLOR) if val == 0 else ("X", CYAN) if val == 1 else ("O", "#FF4A4A")
            if txt: self.canvas_tab4.create_text(x + c_size/2, y + c_size/2, text=txt, fill=color, font=("Segoe UI", 36, "bold"), tags="caro")

    def _on_caro_click(self, event):
        if check_winner(self.caro_board) is not None: return
        cx, cy, c_size, c_gap = 480, 150, 110, 15
        col, row = int((event.x - cx) // (c_size + c_gap)), int((event.y - cy) // (c_size + c_gap))
        
        if 0 <= row < 3 and 0 <= col < 3:
            idx = row * 3 + col
            if self.caro_board[idx] == 0:
                self.caro_board[idx] = 1
                self._append_log(self.tab4_log, f"\nBạn đánh X ở ô ({row}, {col})")
                self.caro_status = "AI đang suy nghĩ..."
                self._draw_caro_board()
                
                if not self._check_caro_end():
                    self.after(200, self._ai_caro_turn)

    def _ai_caro_turn(self):
        """AI tự tính toán điểm tất cả các nút để In Log, thay vì chỉ gọi hàm ẩn bên trong."""
        algo = self.tab4_algo_var.get()
        start_t = time.perf_counter()
        
        self._append_log(self.tab4_log, f"--- AI ({algo}) ĐANG ĐÁNH GIÁ ---")
        best_score = -math.inf
        best_move = -1
        
        for i in range(9):
            if self.caro_board[i] == 0:
                self.caro_board[i] = -1 # AI đi thử nước O
                
                # Tính điểm theo thuật toán
                if "Minimax" in algo:
                    score = minimax(self.caro_board, 0, False)
                else:
                    score = alpha_beta(self.caro_board, 0, -math.inf, math.inf, False)
                    
                self.caro_board[i] = 0 # Khôi phục
                
                # Quy đổi điểm ra kết quả
                kq = "THẮNG" if score > 0 else "THUA" if score < 0 else "HÒA"
                r, c = divmod(i, 3)
                self._append_log(self.tab4_log, f" + Thử ô ({r}, {c}) -> Điểm: {score:2} (Dự đoán: {kq})")
                
                if score > best_score:
                    best_score = score
                    best_move = i
                    
        if best_move != -1:
            self.caro_board[best_move] = -1
            r, c = divmod(best_move, 3)
            self._append_log(self.tab4_log, f"=> AI QUYẾT ĐỊNH ĐÁNH Ô ({r}, {c}) (Time: {round(time.perf_counter() - start_t, 3)}s)")

        self.caro_status = "Lượt của bạn (X)"
        self._draw_caro_board()
        self._check_caro_end()

    def _check_caro_end(self):
        w = check_winner(self.caro_board)
        if w is not None:
            status = "CHÚC MỪNG! BẠN ĐÃ THẮNG AI!" if w == 1 else "AI ĐÃ CHIẾN THẮNG BẠN!" if w == -1 else "TRẬN ĐẤU HÒA NHAU!"
            self.caro_status = status
            self._draw_caro_board()
            self._append_log(self.tab4_log, f"*** {status} ***\n")
            return True
        return False

    def _reset_caro(self):
        self.caro_board = [0]*9; self.caro_status = "Lượt của bạn (X)"
        self._draw_caro_board()
        self._append_log(self.tab4_log, "\nĐã khởi tạo ván mới. Bạn đánh trước (X).")

    # =========================================================================
    # HÀM TIỆN ÍCH CHUNG
    # =========================================================================
    def _draw_puzzle_board(self, canvas, state, tag):
        canvas.delete(tag)
        rounded_rectangle(canvas, self.board_x - 18, self.board_y - 18, self.board_x + self.board_size + 18, self.board_y + self.board_size + 18, radius=28, fill=PANEL_COLOR, outline="#101827", width=2, tags=tag)
        for index, number in enumerate(state):
            if number == 0: continue
            row, col = divmod(index, 4)
            x, y = self.board_x + col * (self.tile_size + self.gap), self.board_y + row * (self.tile_size + self.gap)
            fill_color = TILE_ALT_COLOR if number % 2 == 0 else TILE_COLOR
            rounded_rectangle(canvas, x, y, x + self.tile_size, y + self.tile_size, radius=18, fill=fill_color, outline=TILE_OUTLINE, width=2, tags=tag)
            canvas.create_text(x + self.tile_size / 2, y + self.tile_size / 2, text=str(number), fill=TEXT_COLOR, font=("Segoe UI", 24, "bold"), tags=tag)

    def _draw_mini_board(self, canvas, state, x, y, tag):
        canvas.delete(tag)
        for index, number in enumerate(state):
            row, col = divmod(index, 4)
            tile_x, tile_y = x + col * 35, y + row * 35
            fill_color, txt = (TILE_ALT_COLOR if number % 2 == 0 else TILE_COLOR, str(number)) if number != 0 else (BG_COLOR, "")
            rounded_rectangle(canvas, tile_x, tile_y, tile_x + 28, tile_y + 28, radius=7, fill=fill_color, outline=TILE_OUTLINE if number!=0 else "#172033", width=1, tags=tag)
            if txt: canvas.create_text(tile_x + 14, tile_y + 14, text=txt, fill=TEXT_COLOR, font=("Segoe UI", 8, "bold"), tags=tag)

    def _draw_unknown_mini_board(self, canvas, x, y, tag):
        canvas.delete(tag)
        for index in range(16):
            row, col = divmod(index, 4)
            tile_x, tile_y = x + col * 35, y + row * 35
            rounded_rectangle(canvas, tile_x, tile_y, tile_x + 28, tile_y + 28, radius=7, fill=BG_COLOR, outline=TILE_OUTLINE, width=1, tags=tag)
            canvas.create_text(tile_x + 14, tile_y + 14, text="?", fill=MUTED_TEXT, font=("Segoe UI", 8, "bold"), tags=tag)
        canvas.create_text(x + 52, y + 145, text="No Goal / Unknown", fill=MUTED_TEXT, font=("Segoe UI", 8, "bold"), tags=tag)

    def _normalize_state(self, state):
        try:
            values = tuple(state)
        except TypeError:
            return None
        if len(values) != 16:
            return None
        if not all(isinstance(value, int) for value in values):
            return None
        return values

    def _coerce_state_sequence(self, value):
        state = self._normalize_state(value)
        if state:
            return [state]
        if value is None:
            return []
        states = []
        try:
            iterator = iter(value)
        except TypeError:
            return []
        for item in iterator:
            item_state = self._normalize_state(item)
            if item_state:
                states.append(item_state)
        return states

    def _result_state_sequence(self, result, keys):
        if not isinstance(result, dict):
            return [], None
        for key in keys:
            states = self._coerce_state_sequence(result.get(key))
            if states:
                return states, key
        return [], None

    def _result_state(self, result, keys):
        if not isinstance(result, dict):
            return None
        for key in keys:
            state = self._normalize_state(result.get(key))
            if state:
                return state
        return None

    def _log_tried_states(self, result, keys, label):
        states, key = self._result_state_sequence(result, keys)
        if not states:
            return
        self._append_log(self.tab2_log, f"[{label} - result['{key}']]: {len(states)} trạng thái")
        for idx, state in enumerate(states, 1):
            self._append_log(self.tab2_log, f"{label} {idx}:\n{format_state_grid(state)}\n")

    def update_main_board(self, state):
        """Cập nhật bàn cờ chính của tab Môi trường phức tạp."""
        normalized_state = self._normalize_state(state)
        if not normalized_state:
            return
        self.tab2_state = normalized_state
        self._refresh_tab2_view()

    def update_start_panel(self, state):
        """Cập nhật bảng Start State của tab Môi trường phức tạp."""
        normalized_state = self._normalize_state(state)
        self.canvas_tab2.delete("t2_start_panel")
        self.tab2_start_state = normalized_state
        if normalized_state:
            self._draw_mini_board(self.canvas_tab2, normalized_state, 70, 170, "t2_start_panel")
        else:
            self.canvas_tab2.create_text(140, 236, text="Chưa xác định", fill=MUTED_TEXT, font=("Segoe UI", 10, "bold"), tags="t2_start_panel")

    def update_goal_panel(self, state, unknown=False):
        """Cập nhật bảng Goal State. Nếu unknown=True thì hiển thị dấu hỏi."""
        self.canvas_tab2.delete("t2_goal_panel")
        self.tab2_goal_unknown = unknown
        if unknown:
            self.tab2_goal_state = None
            self._draw_unknown_mini_board(self.canvas_tab2, 70, 402, "t2_goal_panel")
            return
        normalized_state = self._normalize_state(state)
        self.tab2_goal_state = normalized_state
        if normalized_state:
            self._draw_mini_board(self.canvas_tab2, normalized_state, 70, 402, "t2_goal_panel")

    def set_solution_path(self, path, moves=None, owner=None):
        """Lưu path để Play Solution và Next Step dùng lại."""
        self.solution_path = self._coerce_state_sequence(path)
        self.solution_moves = list(moves or [])
        self.solution_step_index = 0
        self.solution_owner = owner if self.solution_path else None

    def _active_solution_owner(self):
        try:
            selected_index = self.notebook.index(self.notebook.select())
        except tk.TclError:
            return self.solution_owner
        if selected_index == 0:
            return "tab1"
        if selected_index == 1:
            return "tab2"
        return None

    def _show_solution_state(self, owner, state, step_index):
        if owner == "tab1":
            self.tab1_state = state
            self.moves = step_index
            self._refresh_tab1_view()
        elif owner == "tab2":
            self.update_main_board(state)

    def _log_tab2_simulation(self, message):
        if self._active_solution_owner() == "tab2":
            self._append_log(self.tab2_log, message)

    def _play_solution(self):
        owner = self._active_solution_owner()
        if owner != self.solution_owner or not self.solution_path:
            if owner == "tab2":
                self._append_log(self.tab2_log, "Chưa có lời giải hoặc danh sách trạng thái để mô phỏng.")
            return
        self.solution_step_index = 0
        self._play_next_state(owner)

    def _play_next_state(self, owner=None):
        owner = owner or self._active_solution_owner()
        if owner != self.solution_owner or not self.solution_path:
            return
        if self.solution_step_index < len(self.solution_path):
            state = self.solution_path[self.solution_step_index]
            self._show_solution_state(owner, state, self.solution_step_index)
            if owner == "tab2":
                self._append_log(self.tab2_log, f"Đang mô phỏng bước {self.solution_step_index}")
            self.solution_step_index += 1
            self.after(350, lambda: self._play_next_state(owner))
        elif owner == "tab2":
            self._append_log(self.tab2_log, "Đã mô phỏng hết đường đi.")

    def _next_step(self):
        owner = self._active_solution_owner()
        if owner != self.solution_owner or not self.solution_path:
            if owner == "tab2":
                self._append_log(self.tab2_log, "Chưa có dữ liệu mô phỏng.")
            return
        step_index = self.solution_step_index
        if owner == "tab2" and step_index == 0 and self.solution_path and self.tab2_state == self.solution_path[0]:
            step_index = 1
        if step_index < len(self.solution_path):
            state = self.solution_path[step_index]
            self._show_solution_state(owner, state, step_index)
            if owner == "tab2":
                self._append_log(self.tab2_log, f"Đang mô phỏng bước {step_index}")
            self.solution_step_index = step_index + 1
        elif owner == "tab2":
            self._append_log(self.tab2_log, "Đã mô phỏng hết đường đi.")

    def _append_log(self, text_widget, message):
        text_widget.config(state="normal")
        text_widget.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        text_widget.see("end")
        text_widget.config(state="disabled")

    def _clear_all_logs(self):
        for widget in [self.tab1_log, self.tab2_log, self.tab3_log, self.tab4_log]:
            widget.config(state="normal"); widget.delete("1.0", "end"); widget.config(state="disabled")
