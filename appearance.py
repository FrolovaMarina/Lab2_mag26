from items import *
from extra import *
from board_data import *
import pygame as pg
import random
import time

import torch
import numpy as np
from logic import Game, encode_board  


pg.init()
font = pg.font.SysFont('calibry', 18, italic=True)


class Playboard:
    def __init__(self, parent_surface: pg.Surface):
        self.__screen = parent_surface
        self.__table = board
        self.__count = CELL_COUNT
        self.__size = CELL_SIZE
        self.__item_types = types
        self.__next_turn = 'white'
        self.__cells_sprite = pg.sprite.Group()
        self.__items_sprite = pg.sprite.Group()
        self.__items_white = []
        self.__items_black = []
        self.__queens_white = []
        self.__queens_black = []
        self.__items_coords = []
        self.__pressed_cell = None
        self.__picked_checker = None
        self.__wCHECK = False
        self.__bCHECK = False
        self.__wqCHECK = False
        self.__bqCHECK = False
        self.__background()
        self.__draw_playboard()
        self.__draw_items()
        
        self.load_model()
        
        self.N = 0
        self.count = 0

        pg.display.update()


    def load_model(self):
        try:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            class ValueNet(torch.nn.Module):
                def __init__(self, input_size=64, hidden_size=64):
                    super().__init__()
                    self.fc1 = torch.nn.Linear(input_size, hidden_size)
                    self.fc2 = torch.nn.Linear(hidden_size, hidden_size)
                    self.fc3 = torch.nn.Linear(hidden_size, 1)
                    self.tanh = torch.nn.Tanh()
                def forward(self, x):
                    x = torch.relu(self.fc1(x))
                    x = torch.relu(self.fc2(x))
                    x = self.fc3(x)
                    return self.tanh(x)
            self.model = ValueNet()
            self.model.load_state_dict(torch.load('value_net.pth', map_location=self.device))
            self.model.eval()
        except Exception as e:
            self.model = None
    
    def __background(self):
        background_image = pg.image.load('images/' + 'Ametist.jpg')
        background_image = pg.transform.scale(background_image, WINDOW_SIZE)
        self.__screen.blit(background_image, (0, 0))
  
    def __draw_playboard(self):
        total_size = self.__count * self.__size
        numbers_fields = self.__numbers_fields()
        self.__cells_sprite = self.__create_cells()
        width = numbers_fields[0].get_width()
        board_view = pg.Surface((2 * width + total_size, 2 * width + total_size), pg.SRCALPHA)
        contour_image = pg.image.load('images/' + 'Sea_contour.jpg')
        contour_image = pg.transform.scale(contour_image, (board_view.get_width(), board_view.get_height()))
        board_view.blit(contour_image, contour_image.get_rect())
        board_view.blit(numbers_fields[0], (0, width))
        board_view.blit(numbers_fields[0], (width + total_size, width))
        board_view.blit(numbers_fields[1], (width, 0))
        board_view.blit(numbers_fields[1], (width, width + total_size))

        board_rect = board_view.get_rect()
        board_rect.x += (self.__screen.get_width() - board_rect.width) // 2
        board_rect.y += (self.__screen.get_height() - board_rect.height) // 2
        self.__screen.blit(board_view, board_rect)
        cells_direction = (board_rect.x + width, board_rect.y + width)
        self.__draw_cells(cells_direction)

    def __numbers_fields(self):
        n_lines = pg.Surface((self.__count * self.__size, self.__size // 2), pg.SRCALPHA)
        n_rows = pg.Surface((self.__size // 2, self.__count * self.__size), pg.SRCALPHA)
        for i in range(0, self.__count):
            letters = font.render(names[i], 1, WHITE)
            number = font.render(str(self.__count - i), 1, WHITE)
            n_lines.blit(letters, (i * self.__size + (self.__size - letters.get_rect().width) // 2,
                                   (n_lines.get_height() - letters.get_rect().height) // 2))
            n_rows.blit(number, ((n_rows.get_width() - letters.get_rect().width) // 2,
                                 i * self.__size + (self.__size - number.get_rect().height) // 2))
        return n_rows, n_lines

    def __create_cells(self):
        group = pg.sprite.Group()
        even_count = (self.__count % 2 == 0)
        cell_colour_index = 1 if even_count else 0
        for y in range(self.__count):
            for x in range(self.__count):
                cells = Cells(cell_colour_index, self.__size, (x, y), names[x] + str(self.__count - y))
                group.add(cells)
                cell_colour_index ^= True
            cell_colour_index = cell_colour_index ^ True if even_count else cell_colour_index
        return group

    def __draw_cells(self, direction):
        for cells in self.__cells_sprite:
            cells.rect.x += direction[0]
            cells.rect.y += direction[1]
        self.__cells_sprite.draw(self.__screen)

    def __draw_items(self):
        self.__run_board()
        self.__black_or_white()
        self.__items_sprite.draw(self.__screen)

    def __run_board(self):
        for j, row in enumerate(self.__table):
            for i, field_value in enumerate(row):
                if field_value != 0:
                    item = self.__create_item(field_value, (j, i))
                    self.__items_sprite.add(item)
        for item in self.__items_sprite:
            for cells in self.__cells_sprite:
                if item.field_name == cells.field_name:
                    item.colour = cells.colour
                    item.rect = cells.rect

    def __create_item(self, item_symbol: str, table_coord: tuple):
        field_name = self.__to_field_name(table_coord)
        item_tuple = self.__item_types[item_symbol]
        classname = globals()[item_tuple[0]]
        return classname(self.__size, item_tuple[0], field_name)

    def __to_field_name(self, table_coord: tuple):
        return names[table_coord[1]] + str(self.__count - table_coord[0])

    def __get_cell(self, position: tuple):
        for cells in self.__cells_sprite:
            if cells.rect.collidepoint(position):
                return cells
        return None

    def button_down(self, button_type: int, position: tuple):
        self.__pressed_cell = self.__get_cell(position)

    def button_up(self, button_type: int, position: tuple):
        released_cell = self.__get_cell(position)
        if (released_cell is not None) and (released_cell == self.__pressed_cell):
            if button_type == 1:
                self.__pick_cell(released_cell)
        self.__update()
   
    def __black_or_white(self):
        for item in self.__items_sprite:
            if item.icolour == Checker1.icolour:
                self.__items_white.append(item.field_name)
            elif item.icolour == Checker2.icolour:
                self.__items_black.append(item.field_name)
        return self.__items_white, self.__items_black

    def __update(self):
        print(" ")
        self.__cells_sprite.draw(self.__screen)
        self.__items_sprite.draw(self.__screen)
        pg.display.update()

    def __pick_cell(self, cells):
        print("Очередь хода у", self.__next_turn)
        if self.__picked_checker is None and self.__next_turn == 'white':
            for item in self.__items_sprite:
                if item.field_name == cells.field_name:
                    self.__picked_checker = item
                    self.__field_checker = item.field_name
                    self.__checker_colour = item.icolour
                    break
        else:
            if cells.colour == 0:
                if self.__next_turn == 'white' and self.__checker_colour == Checker1.icolour:
                    self.__field_cell = cells.field_name
                    self.__CHECK_HITTING = self.__check_hitting()
                    if self.__picked_checker.field_name in self.__queens_white:
                        variants = self.__move_queens(self.__field_checker)
                        self.__qCHECK_HITTING = self.__qcheck_hitting()
                        if self.__wqCHECK is True:
                            if cells.field_name in self.__hiting_move_wqueens(self.__qCHECK_HITTING) and \
                                    self.__picked_checker.field_name == self.__field_checker and \
                                    cells.field_name not in self.__items_white:
                                self.__wqCHECK = False
                                self.__wchecker_step(cells)
                        elif self.__field_cell in variants and self.__wCHECK is False:
                            self.__wchecker_step(cells)
                        elif self.__wCHECK is False:
                            self.__qcheck_hitting()
                        else:
                            self.__picked_checker = None
                    elif self.__wCHECK is True and self.__wqCHECK is False:
                        if len(self.__active_Wcheckers) >= 2:
                            self.__CHECK_HITTING = self.__field_checker
                        if cells.field_name in self.__hiting_move_wcheckers(self.__CHECK_HITTING) and\
                                self.__picked_checker.field_name == self.__field_checker and\
                                cells.field_name not in self.__items_white:
                            self.__wchecker_step(cells)
                        else:
                            self.__picked_checker = None
                    elif cells.field_name in self.__move_wcheckers(self.__field_checker) and \
                            cells.field_name not in self.__items_white and self.N == 0:
                        self.__wchecker_step(cells)
                    else:
                        self.__picked_checker = None
                else:
                    self.__picked_checker = None
            
    def __computer_turn(self):
        board_logic = [[0]*8 for _ in range(8)]
        for item in self.__items_sprite:
            field = item.field_name
            if not field:
                continue
            col = names.index(field[0])      
            row = 8 - int(field[1])
            if item.icolour == WHITE: 
                if isinstance(item, Queen1):
                    board_logic[row][col] = 'W'
                else:
                    board_logic[row][col] = 'w'
            else:                            
                if isinstance(item, Queen2):
                    board_logic[row][col] = 'B'
                else:
                    board_logic[row][col] = 'b'

        state = Game(board_logic, white_turn=False)
        moves = state.possible_moves()       
        if not moves:
            print("Нет ходов")
            return
        if self.model is None:
            chosen_move = random.choice(moves)
        else:
            best_value = -float('inf')
            best_move = None
            for move in moves:
                next_state = state.do_move(move)
                features = np.array(encode_board(next_state.board), dtype=np.float32).reshape(1, -1)
                features_tensor = torch.from_numpy(features).to(self.device)
                with torch.no_grad():
                    value_white = self.model(features_tensor).item()
                black_value = -value_white
                if black_value > best_value:
                    best_value = black_value
                    best_move = move
            chosen_move = best_move if best_move is not None else random.choice(moves)
        from_r, from_c, to_r, to_c, is_capture, cap_r, cap_c = chosen_move
        field_from = names[from_c] + str(8 - from_r)
        field_to   = names[to_c] + str(8 - to_r)
        found = False
        for item in self.__items_sprite:
            if item.field_name == field_from:
                self.__picked_checker = item
                self.__field_checker = field_from
                self.__checker_colour = item.icolour
                found = True
                break
        if not found:
            return
        self.__field_cell = field_to

        if is_capture:
            cap_field = names[cap_c] + str(8 - cap_r)
            for item in self.__items_sprite:
                if item.field_name == cap_field:
                    self.__items_sprite.remove(item)
                    if item.field_name in self.__queens_white:
                        self.__queens_white.remove(item.field_name)
                    if item.field_name in self.__items_white:
                        self.__items_white.remove(item.field_name)
                    break 
        self.__bchecker_step()
       
    def __black_win(self):
        win = pg.display.set_mode((200, 70))
        win.fill((167, 200, 250))
        text_surface = font.render('Чёрные выиграли', True, (75, 0, 130))
        count_surface1 = font.render('Количество ходов:', True, (75, 0, 130))
        count_surface2 = font.render(str(self.count), True, (75, 0, 130))
        win.blit(text_surface, (45, 25))
        win.blit(count_surface1, (25, 40))
        win.blit(count_surface2, (145, 40))
        self.__screen.blit(win, (220, 220))
        self.__update()
        time.sleep(10)
        exit()
 
    def __white_win(self):
        win = pg.display.set_mode((200, 70))
        win.fill((237, 186, 245))
        text_surface = font.render('Белые выиграли', True, (75, 0, 130))
        count_surface1 = font.render('Количество ходов:', True, (75, 0, 130))
        count_surface2 = font.render(str(self.count), True, (75, 0, 130))
        win.blit(text_surface, (45, 25))
        win.blit(count_surface1, (25, 40))
        win.blit(count_surface2, (145, 40))
        self.__screen.blit(win, (220, 220))
        self.__update()
        time.sleep(10)
        exit()
  
    def __the_best_choice(self):
        self.__best_choice = False
        for i in self.__items_black:
            move = list(map(lambda el: el + str(int(i[1]) - 1), DIRECTIONS[i[0]]))
            try:
                for j in move:
                    next_move = list(map(lambda el: el + str(int(j[1]) - 1), DIRECTIONS[j[0]]))
                    if next_move[0] in self.__items_white and j not in self.__items_black and\
                            j not in self.__items_white:
                        self.__field_checker = i
                        self.__field_cell = j
                        self.__best_choice = True
                        break
                    elif next_move[1] in self.__items_white and j not in self.__items_black and\
                            j not in self.__items_white:
                        self.__field_checker = i
                        self.__field_cell = j
                        self.__best_choice = True
                        break
            except Exception:
                continue
           
    def __wchecker_step(self, cells):
        self.__picked_checker.rect = cells.rect
        self.__items_white.remove(self.__picked_checker.field_name)
        self.__picked_checker.field_name = cells.field_name
        self.__items_white.append(cells.field_name)
        if self.__picked_checker.field_name in WHITE_QUEEN_FIELD and\
                self.__field_checker not in self.__queens_white:
            self.__transform_to_queen()
        elif self.__field_checker in self.__queens_white:
            self.__queens_white.remove(self.__field_checker)
            self.__queens_white.append(cells.field_name)
        self.__update()
        if not self.__items_black:
            time.sleep(0.5)
            self.__black_win()
        if self.__wCHECK is True:
            if cells.colour == 0 and self.__checker_colour == Checker1.icolour:
                self.__check_hitting()
                if self.__wCHECK is True:
                    self.__next_turn = 'white'
                    self.N = 1
                else:
                    self.N = 0
                    self.__picked_checker = None
                    self.__next_turn = 'black'
        else:
            self.N = 0
            self.__picked_checker = None
            self.__next_turn = 'black'
        print("*Ход белых сделан*")
        print(" ")
        print("*Очередь хода у", self.__next_turn, "*")
        self.count += 1
        self.__update()
        time.sleep(0.5)
        if self.__next_turn == 'black':
            self.__computer_turn()
       
    def __bchecker_step(self):
        for cell in self.__cells_sprite:
            if cell.field_name == self.__field_cell:
                self.__picked_checker.rect = cell.rect
                break
        self.__items_black.remove(self.__picked_checker.field_name)
        self.__picked_checker.field_name = self.__field_cell
        self.__items_black.append(self.__field_cell)
        if self.__picked_checker.field_name in BLACK_QUEEN_FIELD and\
               self.__field_checker not in self.__queens_black:
            self.__transform_to_queen()
        elif self.__field_checker in self.__queens_black:
            self.__queens_black.remove(self.__field_checker)
            self.__queens_black.append(self.__field_cell)
        self.__update()
        if not self.__items_white:
            time.sleep(0.5)
            self.__white_win()
        if self.__bCHECK is True:
            self.__check_hitting()
            if self.__bCHECK is True and self.__picked_checker.field_name in self.__active_Bcheckers and\
                    self.__picked_checker.field_name not in self.__queens_black:
                time.sleep(0.5)
                self.__field_checker = self.__picked_checker.field_name
                self.__field_cell = random.choice(self.__hiting_move_bcheckers(self.__CHECK_HITTING))
                self.__bchecker_step()
            elif self.__picked_checker.field_name in self.__queens_black:
                self.__qCHECK_HITTING = self.__qcheck_hitting()
                if self.__bqCHECK is True:
                    self.__field_checker = self.__picked_checker.field_name
                    time.sleep(0.5)
                    self.__computer_turn()
        self.N = 0
        self.__picked_checker = None
        self.__next_turn = 'white'
        print("*Ход чёрных сделан*")
   
    def __move_wcheckers(self, field_name):
        directions = DIRECTIONS[field_name[0]]
        moves = list(map(lambda el: el + str(int(field_name[1]) + 1), directions))
        return moves

    def __move_queens(self, field_name):
        self.__diagonal_1 = []
        self.__diagonal_2 = []
        self.__diagonal_3 = []
        self.__diagonal_4 = []
        variants = []
        self.__all = []
        q = QUEEN_DIRECTIONS[field_name[0]]
        n = 0
        while n < len(q):
            for i in range(1, len(q) + 1):
                try:
                    self.__q_moves1 = list(map(lambda el: el + str(int(field_name[1]) + i), q[n]))
                    self.__q_moves2 = list(map(lambda el: el + str(int(field_name[1]) - i), q[n]))
                    if self.__q_moves1[0] in FIELD:
                        self.__all.append(self.__q_moves1[0])
                        self.__diagonal_1.append(self.__q_moves1[0])
                        if self.__q_moves1[0] not in self.__items_white and\
                                self.__q_moves1[0] not in self.__items_black:
                            variants.append(self.__q_moves1[0])
                    if self.__q_moves2[0] in FIELD:
                        self.__all.append(self.__q_moves2[0])
                        self.__diagonal_2.append(self.__q_moves2[0])
                        if self.__q_moves2[0] not in self.__items_white and\
                                self.__q_moves2[0] not in self.__items_black:
                            variants.append(self.__q_moves2[0])
                    if self.__q_moves1[1] in FIELD:
                        self.__all.append(self.__q_moves1[1])
                        self.__diagonal_3.append(self.__q_moves1[1])
                        if self.__q_moves1[1] not in self.__items_white and\
                                self.__q_moves1[1] not in self.__items_black:
                            variants.append(self.__q_moves1[1])
                    if self.__q_moves2[1] in FIELD:
                        self.__all.append(self.__q_moves2[1])
                        self.__diagonal_4.append(self.__q_moves2[1])
                        if self.__q_moves2[1] not in self.__items_white and\
                                self.__q_moves2[1] not in self.__items_black:
                            variants.append(self.__q_moves2[1])
                except Exception:
                    pass
                n += 1
        return variants

    def __hiting_move_wcheckers(self, field_name):
        if self.__field_checker not in self.__active_Wcheckers:
            return field_name
        step_backward = list(map(lambda el: el + str(int(field_name[1]) - 1), DIRECTIONS[field_name[0]]))
        step_forward = self.__move_wcheckers(field_name)
        result = step_forward + step_backward
        for i in result:
            if i in self.__items_black:
                try:
                    if i[0] in HIT_DIRECTIONS[field_name[0]].keys():
                        self.__jump_forward = HIT_DIRECTIONS[field_name[0]][i[0]] + str(int(field_name[1]) + 2)
                        self.__jump_backward = HIT_DIRECTIONS[field_name[0]][i[0]] + str(int(field_name[1]) - 2)
                    if i in step_forward and self._Wforward_jump == 1 and\
                            self.__jump_forward not in self.__items_black and self.__jump_forward in FIELD and\
                            i[0] in self.i:
                        if self.__field_cell == self.__jump_forward:
                            result.clear()
                            result.append(self.__jump_forward)
                            for item in self.__items_sprite:
                                if item.field_name == i:
                                    self.__items_sprite.remove(item)
                                    if item.field_name in self.__queens_black:
                                        self.__queens_black.remove(item.field_name)
                                    self.__items_black.remove(item.field_name)
                                    return result
                        elif self.__field_cell not in self.__can_Fjump:
                            return field_name
                    if i in step_backward and self._Wback_jump == 1 and\
                            self.__jump_backward not in self.__items_black and self.__jump_backward in FIELD and\
                            i[0] in self.i:
                        step_backward.append(self.__jump_backward)
                        if self.__field_cell == self.__jump_backward:
                            for item in self.__items_sprite:
                                if item.field_name == i:
                                    self.__items_sprite.remove(item)
                                    if item.field_name in self.__queens_black:
                                        self.__queens_black.remove(item.field_name)
                                    self.__items_black.remove(item.field_name)
                                    return step_backward
                        elif self.__field_cell not in self.__can_Bjump:
                            return field_name
                except Exception:
                    break
               
    def __hiting_move_wqueens(self, field_name):
        if self.__field_checker not in self.__active_Wqueens:
            return field_name
        step = self.__move_queens(field_name)
        not_hit = []
        for i in self.__diagonal:
            if i != self.Q:
                not_hit.append(i)
            else:
                hit = list(set(self.__diagonal) - set(not_hit))
                step.clear()
                step.append(hit)
                if self.__field_cell in hit and self.__field_cell != self.Q and\
                        self.__field_cell not in self.__items_white:
                    for item in self.__items_sprite:
                        if item.field_name == i:
                            self.__items_sprite.remove(item)
                            self.__items_black.remove(item.field_name)
                            if item.field_name in self.__queens_black:
                                self.__queens_black.remove(item.field_name)
                            return hit
                else:
                    return step
           
    def __hiting_move_bqueens(self, field_name):
        not_hit = []
        for i in self.__diagonal:
            if i != self.Q:
                not_hit.append(i)
            else:
                hit = list(set(self.__diagonal) - set(not_hit))
                for h in hit:
                    if h in self.__items_black or h in self.__items_white:
                        hit.remove(h)
                    if self.Q in hit:
                        hit.remove(self.Q)
                for item in self.__items_sprite:
                    if item.field_name == i:
                        if not hit:
                            self.__bqCHECK = False
                            return field_name
                        self.__items_sprite.remove(item)
                        self.__items_white.remove(item.field_name)
                        if item.field_name in self.__queens_white:
                            self.__queens_white.remove(item.field_name)
                        hit_field = random.choice(hit)
                        return hit_field
                 
    def __move_bcheckers(self, field_name):
        directions = DIRECTIONS[field_name[0]]
        moves = list(map(lambda el: el + str(int(field_name[1]) - 1), directions))
        return moves

    def __hiting_move_bcheckers(self, field_name):
        field_name = self.__field_checker
        if self.__field_checker[1] != 8:
            step_backward = list(map(lambda el: el + str(int(field_name[1]) + 1), DIRECTIONS[field_name[0]]))
        else:
            step_backward = []
        step_forward = self.__move_bcheckers(field_name)
        result = step_forward + step_backward
        for i in result:
            if i in self.__items_white:
                try:
                    if i[0] in HIT_DIRECTIONS[field_name[0]].keys():
                        self.__jump_forward = HIT_DIRECTIONS[field_name[0]][i[0]] + str(int(field_name[1]) - 2)
                        self.__jump_backward = HIT_DIRECTIONS[field_name[0]][i[0]] + str(int(field_name[1]) + 2)
                    if i in step_forward and self.__jump_forward not in self.__items_white and\
                            self._Bforward_jump == 1 and self.__jump_forward in FIELD:
                        result.clear()
                        result.append(self.__jump_forward)
                        for item in self.__items_sprite:
                            if item.field_name == i:
                                self.__items_sprite.remove(item)
                                if item.field_name in self.__queens_white:
                                    self.__queens_white.remove(item.field_name)
                                self.__items_white.remove(item.field_name)
                                return result
                    if i in step_backward and self.__jump_backward not in self.__items_white and\
                            self._Bback_jump == 1 and self.__jump_backward in FIELD:
                        step_backward.clear()
                        step_backward.append(self.__jump_backward)
                        for item in self.__items_sprite:
                            if item.field_name == i:
                                self.__items_sprite.remove(item)
                                if item.field_name in self.__queens_white:
                                    self.__queens_white.remove(item.field_name)
                                self.__items_white.remove(item.field_name)
                                return step_backward
                        else:
                            return step_backward
                    else:
                        continue
                except Exception:
                    break

    def __create_a_queen(self, item_symbol: str):
        field_name = self.__picked_checker.field_name
        item_tuple = self.__item_types[item_symbol]
        classname = globals()[item_tuple[0]]
        return classname(self.__size, item_tuple[0], field_name)

    def __transform_to_queen(self):
        for item in self.__items_sprite:
            if item.field_name == self.__picked_checker.field_name:
                self.__items_sprite.remove(item)
                for k in types.keys():
                    if k == 'Q' and item.field_name in self.__items_white:
                        queen = self.__create_a_queen(k)
                        self.__items_sprite.add(queen)
                        queen.rect = item.rect
                        self.__queens_white.append(queen.field_name)
                        self.__items_white.append(queen.field_name)
                        self.__items_white.remove(item.field_name)
                    elif k == 'q' and item.field_name in self.__items_black:
                        queen = self.__create_a_queen(k)
                        self.__items_sprite.add(queen)
                        queen.rect = item.rect
                        self.__queens_black.append(queen.field_name)
                        self.__items_black.append(queen.field_name)
                        self.__items_black.remove(item.field_name)

    def __check_hitting(self):
        if self.__next_turn == 'white':
            self.__active_Wcheckers = []
            self._Wforward_jump = 0
            self._Wback_jump = 0
            self.__can_Fjump = []
            self.__can_Bjump = []
            self.i = []
            for field in self.__items_white:
                forward = self.__move_wcheckers(field)
                back = list(map(lambda el: el + str(int(field[1]) - 1), DIRECTIONS[field[0]]))
                near = forward + back
                for any_checker in near:
                    try:
                        if any_checker[0] in HIT_DIRECTIONS[field[0]].keys():
                            self.__jump_forward = HIT_DIRECTIONS[field[0]][any_checker[0]] + str(int(field[1]) + 2)
                            self.__jump_backward = HIT_DIRECTIONS[field[0]][any_checker[0]] + str(int(field[1]) - 2)
                            if any_checker in self.__items_black:
                                if any_checker in forward and self.__jump_forward not in self.__items_black and\
                                        self.__jump_forward not in self.__items_white and\
                                        self.__jump_forward in FIELD:
                                    self.__can_Fjump.append(self.__jump_forward)
                                    self.__active_Wcheckers.append(field)
                                    self.__field = field
                                    self._Wforward_jump = 1
                                    self.i.append(any_checker[0])
                                if any_checker in back and self.__jump_backward not in self.__items_black and\
                                        self.__jump_backward not in self.__items_white and\
                                        self.__jump_backward in FIELD:
                                    self.__can_Bjump.append(self.__jump_backward)
                                    self.__active_Wcheckers.append(field)
                                    self.__field = field
                                    self._Wback_jump = 1
                                    self.i.append(any_checker[0])
                    except Exception:
                        break
            if len(self.__active_Wcheckers) == 1:
                self.__wCHECK = True
                return self.__field
            elif len(self.__active_Wcheckers) >= 2:
                self.__wCHECK = True
                return self.__active_Wcheckers
            else:
                self.__wCHECK = False
        elif self.__next_turn == 'black':
            self.__active_Bcheckers = []
            for field in self.__items_black:
                forward = self.__move_bcheckers(field)
                back = list(map(lambda el: el + str(int(field[1]) + 1), DIRECTIONS[field[0]]))
                near = forward + back
                for any_checker in near:
                    try:
                        if any_checker[0] in HIT_DIRECTIONS[field[0]].keys():
                            self.__jump_forward = HIT_DIRECTIONS[field[0]][any_checker[0]] + str(int(field[1]) - 2)
                            self.__jump_backward = HIT_DIRECTIONS[field[0]][any_checker[0]] + str(int(field[1]) + 2)
                            if any_checker in self.__items_white:
                                if any_checker in forward and self.__jump_forward not in self.__items_black and \
                                        self.__jump_forward not in self.__items_white and \
                                        self.__jump_forward in FIELD:
                                    self.__active_Bcheckers.append(field)
                                    self.__field = field
                                    self._Bforward_jump = 1
                                elif any_checker in back and self.__jump_backward not in self.__items_black and \
                                        self.__jump_backward not in self.__items_white and \
                                        self.__jump_backward in FIELD:
                                    self.__active_Bcheckers.append(field)
                                    self.__field = field
                                    self._Bback_jump = 1
                    except Exception:
                        break
            if len(self.__active_Bcheckers) == 1:
                self.__bCHECK = True
                return self.__field
            elif len(self.__active_Bcheckers) >= 2:
                self.__bCHECK = True
                return self.__active_Bcheckers
            else:
                self.__bCHECK = False

    def __qcheck_hitting(self):
        if self.__next_turn == 'white':
            self.__active_Wqueens = []
            self.__diagonal = []
            for field in self.__queens_white:
                for any_item in self.__all:
                    if any_item in self.__items_black:
                        try:
                            forward = self.__move_bcheckers(any_item)
                            back = list(map(lambda el: el + str(int(any_item[1]) + 1), DIRECTIONS[any_item[0]]))
                            if any_item in self.__diagonal_1 and\
                                    back[0] not in self.__items_black and forward[1] not in self.__items_black:
                                self.__diagonal = self.__diagonal_1
                                self.Q = any_item
                                self.__active_Wcheckers.append(field)
                                self.__active_Wqueens.append(field)
                                self.__field = field
                                break
                            elif any_item in self.__diagonal_2 and\
                                    back[1] not in self.__items_black and forward[0] not in self.__items_black:
                                self.__diagonal = self.__diagonal_2
                                self.Q = any_item
                                self.__active_Wcheckers.append(field)
                                self.__active_Wqueens.append(field)
                                self.__field = field
                                break
                            elif any_item in self.__diagonal_3 and back[1] not in self.__items_black and\
                                    forward[0] not in self.__items_black:
                                self.__diagonal = self.__diagonal_3
                                self.Q = any_item
                                self.__active_Wcheckers.append(field)
                                self.__active_Wqueens.append(field)
                                self.__field = field
                                break
                            elif any_item in self.__diagonal_4 and back[0] not in self.__items_black and\
                                    forward[1] not in self.__items_black:
                                self.__diagonal = self.__diagonal_4
                                self.Q = any_item
                                self.__active_Wqueens.append(field)
                                self.__active_Wcheckers.append(field)
                                self.__field = field
                                break
                        except Exception:
                            print(" ")
            if len(self.__active_Wqueens) >= 1:
                for j in self.__diagonal:
                    for k in self.__items_white:
                        if j == k:
                            self.__wqCHECK = False
                        else:
                            self.__wqCHECK = True
                            return self.__field
            else:
                self.__wqCHECK = False
        elif self.__next_turn == 'black':
            self.__active_Bqueens = []
            self.__diagonal = []
            for field in self.__queens_black:
                self.__move_queens(field)
                for any_item in self.__all:
                    if any_item in self.__items_white:
                        try:
                            forward = self.__move_wcheckers(any_item)
                            back = list(map(lambda el: el + str(int(any_item[1]) - 1), DIRECTIONS[any_item[0]]))
                            if any_item in self.__diagonal_1 and\
                                    back[1] not in self.__items_white and forward[0] not in self.__items_white:
                                self.__diagonal = self.__diagonal_1
                                self.Q = any_item
                                self.__active_Bqueens.append(field)
                                self.__field = field
                                break
                            elif any_item in self.__diagonal_2 and\
                                    back[0] not in self.__items_white and forward[1] not in self.__items_white:
                                self.__diagonal = self.__diagonal_2
                                self.Q = any_item
                                self.__active_Bqueens.append(field)
                                self.__field = field
                                break
                            elif any_item in self.__diagonal_3 and\
                                    back[0] not in self.__items_white and forward[1] not in self.__items_white:
                                self.__diagonal = self.__diagonal_3
                                self.Q = any_item
                                self.__active_Bqueens.append(field)
                                self.__field = field
                                break
                            elif any_item in self.__diagonal_4 and\
                                    back[1] not in self.__items_white and forward[0] not in self.__items_white:
                                self.__diagonal = self.__diagonal_4
                                self.Q = any_item
                                self.__active_Bqueens.append(field)
                                self.__field = field
                                break
                        except Exception:
                            print(" ")
            if len(self.__active_Bqueens) >= 1:
                for j in self.__diagonal:
                    for k in self.__items_black:
                        if j == k:
                            self.__bqCHECK = False
                        else:
                            self.__bqCHECK = True
                            return self.__field
            else:
                self.__bqCHECK = False


class Cells(pg.sprite.Sprite):
    def __init__(self, colour_index: int, size: int, coords: tuple, name: str):
        super().__init__()
        x, y = coords
        self.colour = colour_index
        self.field_name = name
        self.image = pg.image.load(COLOURS[colour_index])
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = pg.Rect(x * size, y * size, size, size)
