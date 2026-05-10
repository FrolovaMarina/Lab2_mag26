import copy
import numpy as np

class Game:
    def __init__(self, board=None, white_turn=True):
        if board is None:
            self.board = [
                [0, 'b', 0, 'b', 0, 'b', 0, 'b'],
                ['b', 0, 'b', 0, 'b', 0, 'b', 0],
                [0, 'b', 0, 'b', 0, 'b', 0, 'b'],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                ['w', 0, 'w', 0, 'w', 0, 'w', 0],
                [0, 'w', 0, 'w', 0, 'w', 0, 'w'],
                ['w', 0, 'w', 0, 'w', 0, 'w', 0]
            ]
        else:
            self.board = copy.deepcopy(board)
        self.white_turn = white_turn 

    def possible_moves(self):
        all_moves = []
        captures = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == 0:
                    continue
                if self.white_turn and piece in ('w', 'W'):
                    piece_moves = self._get_moves(r, c)
                elif not self.white_turn and piece in ('b', 'B'):
                    piece_moves = self._get_moves(r, c)
                else:
                    continue
                for move in piece_moves:
                    if move[4]: 
                        captures.append(move)
                    else:
                        all_moves.append(move)
        if captures:
            return captures
        return all_moves

    def _get_moves(self, r, c):
        piece = self.board[r][c]
        moves = []
        if piece == 'w':  
            for dr, dc in [(-1, -1), (-1, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == 0:
                    moves.append((r, c, nr, nc, False, None, None))
        elif piece == 'b':  
            for dr, dc in [(1, -1), (1, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == 0:
                    moves.append((r, c, nr, nc, False, None, None))
        elif piece in ('W', 'B'):   
            for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    if self.board[nr][nc] == 0:
                        moves.append((r, c, nr, nc, False, None, None))
                    else:
                        break
                    nr += dr
                    nc += dc

        captures = self._get_captures(r, c)
        moves.extend(captures)
        return moves

    def _get_captures(self, r, c):
        piece = self.board[r][c]
        captures = []
        if piece == 'w':  
            for dr, dc in [(-1, -1), (-1, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] in ('b', 'B'):
                    nnr, nnc = nr + dr, nc + dc
                    if 0 <= nnr < 8 and 0 <= nnc < 8 and self.board[nnr][nnc] == 0:
                        captures.append((r, c, nnr, nnc, True, nr, nc))
        elif piece == 'b':  
            for dr, dc in [(1, -1), (1, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] in ('w', 'W'):
                    nnr, nnc = nr + dr, nc + dc
                    if 0 <= nnr < 8 and 0 <= nnc < 8 and self.board[nnr][nnc] == 0:
                        captures.append((r, c, nnr, nnc, True, nr, nc))
        elif piece in ('W', 'B'):   
            for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    if self.board[nr][nc] != 0:
                        if (piece == 'W' and self.board[nr][nc] in ('b', 'B')) or \
                           (piece == 'B' and self.board[nr][nc] in ('w', 'W')):
                            nnr, nnc = nr + dr, nc + dc
                            if 0 <= nnr < 8 and 0 <= nnc < 8 and self.board[nnr][nnc] == 0:
                                captures.append((r, c, nnr, nnc, True, nr, nc))
                        break   
                    nr += dr
                    nc += dc
        return captures

    def do_move(self, move):
        new_state = Game(self.board, not self.white_turn)
        from_r, from_c, to_r, to_c, is_capture, cap_r, cap_c = move
        piece = new_state.board[from_r][from_c]
        new_state.board[to_r][to_c] = piece
        new_state.board[from_r][from_c] = 0
        if is_capture:
            new_state.board[cap_r][cap_c] = 0
        if piece == 'w' and to_r == 0:
            new_state.board[to_r][to_c] = 'W'
        elif piece == 'b' and to_r == 7:
            new_state.board[to_r][to_c] = 'B'
        return new_state

    def is_game_over(self):
        return len(self.possible_moves()) == 0

    def result(self):
        white_state = Game(self.board, white_turn=True)
        black_state = Game(self.board, white_turn=False)
        white_moves = white_state.possible_moves()
        black_moves = black_state.possible_moves()
        if len(white_moves) == 0:
            return -1   
        if len(black_moves) == 0:
            return 1    
        return 0   

def encode_board(board):
    flat = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == 0:
                flat.append(0)
            elif p == 'w':
                flat.append(1)
            elif p == 'W':
                flat.append(2)
            elif p == 'b':
                flat.append(-1)
            elif p == 'B':
                flat.append(-2)
    return flat

def encode_board_for_torch(board):
    return np.array(encode_board(board), dtype=np.float32)
