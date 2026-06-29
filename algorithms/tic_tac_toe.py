import math

def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != 0:
            return board[condition[0]]
    if 0 not in board: return 0
    return None

# --- MINIMAX THUẦN TÚY ---
def minimax(board, depth, is_maximizing):
    winner = check_winner(board)
    if winner == 1: return -10 + depth
    if winner == -1: return 10 - depth
    if winner == 0: return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if board[i] == 0:
                board[i] = -1
                best_score = max(minimax(board, depth + 1, False), best_score)
                board[i] = 0
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == 0:
                board[i] = 1
                best_score = min(minimax(board, depth + 1, True), best_score)
                board[i] = 0
        return best_score

def get_best_move_minimax(board):
    best_score = -math.inf
    best_move = -1
    for i in range(9):
        if board[i] == 0:
            board[i] = -1
            score = minimax(board, 0, False)
            board[i] = 0
            if score > best_score:
                best_score, best_move = score, i
    return best_move

# --- ALPHA-BETA PRUNING ---
def alpha_beta(board, depth, alpha, beta, is_maximizing):
    winner = check_winner(board)
    if winner == 1: return -10 + depth
    if winner == -1: return 10 - depth
    if winner == 0: return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if board[i] == 0:
                board[i] = -1
                score = alpha_beta(board, depth + 1, alpha, beta, False)
                board[i] = 0
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha: break # Cắt tỉa nhánh Alpha
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == 0:
                board[i] = 1
                score = alpha_beta(board, depth + 1, alpha, beta, True)
                board[i] = 0
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha: break # Cắt tỉa nhánh Beta
        return best_score

def get_best_move_alpha_beta(board):
    best_score = -math.inf
    best_move = -1
    alpha, beta = -math.inf, math.inf
    for i in range(9):
        if board[i] == 0:
            board[i] = -1
            score = alpha_beta(board, 0, alpha, beta, False)
            board[i] = 0
            if score > best_score:
                best_score, best_move = score, i
            alpha = max(alpha, best_score)
    return best_move