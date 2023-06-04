# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2
import numpy as np
import sys
from sys import stdin
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self):
        self.board = np.full((10, 10), '.', dtype=str)
        self.is_wrong = False #variable to keep track if board reached a wrong/impossible state
        np.set_printoptions(formatter={'str_kind': lambda x: x})
        
    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if(row<0 or row>9 or col<0 or col>9):
            return 'w'
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        if(row<1):
            v1 = 'w'
            v2 = self.board[row+1][col]
        elif(row>8):
            v2 = 'w'
            v1 = self.board[row-1][col]
        else:
            v1 = self.board[row-1][col]
            v2 = self.board[row+1][col]
        return v1, v2

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        if(col<1):
            v1 = 'w'
            v2 = self.board[row][col+1]
        elif(col>8):
            v2 = 'w'
            v1 = self.board[row][col-1]
        else:
            v1 = self.board[row][col-1]
            v2 = self.board[row][col+1]
        return v1, v2
        
    def print(self):
        for i in self.board:
            for j in i:
                if (j == 'w'):
                    print('~', end = '')
                else:
                    print(j, end = '')
            print()       
        

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board."""
        
        lines = stdin.readlines()
        x = 0
        for line in lines:
            lines[x] = line.split()  # Split line into elements based on spaces
            x += 1
        
        board = Board()  # Create a Board instance
        
        #dicionario com os barcos que ja estao completos
        board.completed_boats = {"couracado": 1, 
                                 "cruzadores": 2, 
                                 "contratorpedeiros": 3,
                                 "submarines": 4}
        board.row_array = [int(i) for i in lines[0][1:]] #row hints array
        board.col_array = [int(i) for i in lines[1][1:]] #column hints array
        board.empty_row_array = 10*[10] 
        board.empty_col_array = 10*[10] 
        num_hints = int(lines[2][0])
        board.M_list = []
        
        for i in range(3, 3 + num_hints):
            row = int(lines[i][1])
            col = int(lines[i][2])
            value = lines[i][3]
            if value != 'W':
                board.process_hint(row, col, value)
            else:
                board.put_water(row, col)
                board.board[row][col] = value
                
        board.fill_completed_lines_with_water()
        return board
 
    def process_hint(self, row:int, col:int, hint:str):
        if(self.get_value(row, col) == '.'): #checks if it was previously filled with another hint
            #updates row/col values
            self.row_array[row] -= 1
            self.col_array[col] -= 1
            self.empty_row_array[row] -= 1
            self.empty_col_array[col] -= 1
            #places water in the corners
            self.put_water(row-1, col-1)
            self.put_water(row-1, col+1)
            self.put_water(row+1, col-1)
            self.put_water(row+1, col+1)
        self.board[row][col] = hint

        if hint == 'M': # 'M' clues wont be fully processed during parsing
            adj_values = (self.adjacent_horizontal_values(row, col), self.adjacent_vertical_values(row, col))
            done = False
            for i in range(4):
                if adj_values[i] not in ('w', 'w', '.'):
                    self.process_M_adj(row, col, i)
                    done = True
                    break
            if ~done:
                self.M_list.append((row, col))
        elif hint == 'R':
            self.put_water(row, col+1)
            self.put_water(row-1, col)
            self.put_water(row+1, col)
            aux1 = self.get_value(row, col-1)
            if aux1 == '.':
                aux2 = self.get_value(row, col-2)
                if aux2 == '.': # caso ..R ou Lm.R
                    self.put_boat_piece(row, col-1)
                else: # caso .M.R
                    self.put_boat_piece(row, col-1)
                    self.put_boat_piece(row, col-3)
            elif aux1 == 'L': # caso LR
                self.complete_boat(2)
            elif aux1 == 'M':
                aux2 = self.get_value(row, col-2)
                if aux2 == '.': # caso .MR
                    self.put_boat_piece(row, col-2)
                elif aux2 == 'L': #caso LMR
                    self.complete_boat(3)
            elif aux1 == 'm':
                aux2 = self.get_value(row, col-2)
                if aux2 == 'L': # caso LmR
                    self.complete_boat(3)
                else: # caso LMmR
                    self.complete_boat(4)
        elif hint == 'L':
            self.put_water(row, col-1)
            self.put_water(row-1, col)
            self.put_water(row+1, col)
            aux1 = self.get_value(row, col+1)
            if aux1 == '.':
                aux2 = self.get_value(row, col+2)
                if aux2 == '.': # caso L.. ou L.mR
                    self.put_boat_piece(row, col+1)
                else: # caso L.M.
                    self.put_boat_piece(row, col+1)
                    self.put_boat_piece(row, col+3)
            elif aux1 == 'R': # caso LR
                self.complete_boat(2)
            elif aux1 == 'M':
                aux2 = self.get_value(row, col+2)
                if aux2 == '.': # caso LM.
                    self.put_boat_piece(row, col+2)
                elif aux2 == 'R': #caso LMR
                    self.complete_boat(3)
            elif aux1 == 'm':
                aux2 = self.get_value(row, col+2)
                if aux2 == 'R': # caso LmR
                    self.complete_boat(3)
                else: # caso LmMR
                    self.complete_boat(4)
        elif hint == 'B':
            self.put_water(row, col-1)
            self.put_water(row, col+1)
            self.put_water(row+1, col)
            aux1 = self.get_value(row-1, col)
            if aux1 == '.':
                aux2 = self.get_value(row-2, col)
                if aux2 == '.': # caso ..B ou Tm.B
                    self.put_boat_piece(row-1, col)
                else: # caso .M.R
                    self.put_boat_piece(row-1, col)
                    self.put_boat_piece(row-3, col)
            elif aux1 == 'T': # caso TB
                self.complete_boat(2)
            elif aux1 == 'M':
                aux2 = self.get_value(row-2, col)
                if aux2 == '.': # caso .MB
                    self.put_boat_piece(row-2, col)
                elif aux2 == 'T': #caso TMB
                    self.complete_boat(3)
            elif aux1 == 'm':
                aux2 = self.get_value(row-2, col)
                if aux2 == 'T': # caso TmB
                    self.complete_boat(3)
                else: # caso TMmB
                    self.complete_boat(4)
        elif hint == 'T':
            self.put_water(row, col-1)
            self.put_water(row, col+1)
            self.put_water(row-1, col)
            aux1 = self.get_value(row+1, col)
            if aux1 == '.':
                aux2 = self.get_value(row+2, col)
                if aux2 == '.': # caso T.. ou T.mB
                    self.put_boat_piece(row+1, col)
                else: # caso .M.R
                    self.put_boat_piece(row+1, col)
                    self.put_boat_piece(row+3, col)
            elif aux1 == 'B': # caso TB
                self.complete_boat(2)
            elif aux1 == 'M':
                aux2 = self.get_value(row+2, col)
                if aux2 == '.': # caso TM.
                    self.put_boat_piece(row+2, col)
                elif aux2 == 'B': #caso TMB
                    self.complete_boat(3)
            elif aux1 == 'm':
                aux2 = self.get_value(row+2, col)
                if aux2 == 'B': # caso TmB
                    self.complete_boat(3)
                else: # caso TmMB
                    self.complete_boat(4)
        else:
            self.put_water(row, col-1)
            self.put_water(row, col+1)
            self.put_water(row-1, col)
            self.put_water(row+1, col)
            self.complete_boat(1)
    
    def process_M_adj(self, row: int, col: int, dir :int):
        """recebe pos(row, col) e um int (dir) que representa a direcao na qual o M tem um adjacente"""
        if dir == 0:
            pos = self.get_value(row, col-1)
            if pos in ('m', 'L'):
                self.put_boat_piece(row, col+1)
            elif pos == 'M':
                self.put_boat_piece(row, col-2)
                self.put_boat_piece(row, col+1)
        elif dir == 1:
            pos = self.get_value(row, col+1)
            if pos in ('m', 'R'):
                self.put_boat_piece(row, col-1)
            elif pos == 'M':
                self.put_boat_piece(row, col+2)
                self.put_boat_piece(row, col-1)
        elif dir == 2:
            pos = self.get_value(row-1, col)
            if pos in ('m', 'T'):
                self.put_boat_piece(row+1, col)
            elif pos == 'M':
                self.put_boat_piece(row-2, col)
                self.put_boat_piece(row+1, col)
        elif dir == 3:
            pos = self.get_value(row+1, col)
            if pos in ('m', 'B'):
                self.put_boat_piece(row-1, col)
            elif pos == 'M':
                self.put_boat_piece(row+2, col)
                self.put_boat_piece(row-1, col)

    def fill_completed_lines_with_water(self):
        for i in range(10):
            if self.row_array[i] == 0 and self.empty_row_array[i] > 0:
                for col in range(10):
                    if self.get_value(i, col) == '.':
                        self.put_water(i, col)
            if self.col_array[i] == 0 and self.empty_col_array[i] > 0:
                for row in range(10):
                    if self.get_value(row, i) == '.':
                        self.put_water(row, i)
    
    def complete_boat(self, size: int):
        if size == 1:
            self.completed_boats['submarines'] -= 1
        elif size == 2:
            self.completed_boats['contratorpedeiros'] -= 1
            if self.completed_boats['contratorpedeiros'] == 0:
                self.check_completed_boats()
        elif size == 3:
            self.completed_boats['cruzadores'] -= 1
            if self.completed_boats['cruzadores'] == 0:
                self.check_completed_boats()
        else:
            self.completed_boats['couracado'] -= 1
            if self.completed_boats['couracado'] == 0:
                self.check_completed_boats()
    
    def check_boat_left(self, row: int, col: int):
        """Verifica se ha pecas de barco para a esquerda e, caso haja, se o barco termina """
        res = 1
        if(self.get_value(row, col) in ('l', 'L')):
            return(None, True)
        pos = self.get_value(row, col-res)
        while(res<4 and pos!='.' and pos!='w' and pos!='W'):
            res += 1
            pos = self.get_value(row, col-res)
        
        if(res < 2):
            return (None, False)
        return (res, self.get_value(row, col-res+1) == 'l' or self.get_value(row, col-res+1) == 'L')
    
    def check_boat_right(self, row: int, col: int):
        """Verifica se ha pecas de barco para a direita e, caso haja, se o barco termina """
        res = 1
        if(self.get_value(row, col) in ('r', 'R')):
            return(None, True)
        pos = self.get_value(row, col+res)
        while(res<4 and pos!='.' and pos!='w' and pos!='W'):
            res += 1
            pos = self.get_value(row, col+res)

        if(res < 2):
            return (None, False)
        return (res, self.get_value(row, col+res-1) == 'r' or self.get_value(row, col+res-1) == 'R')
        
    def check_boat_horizontal(self, row:int, col: int):
        """checks for an horizontal boat and returns (size, ends_left:Boolean, ends_right:Boolean)"""
        cbl = self.check_boat_left(row, col)
        cbr = self.check_boat_right(row, col)
        if(cbl[0]==None and cbr[0]==None):
            return (None, False, False)
        elif(cbr[0]==None):
            return (cbl[0], cbl[1], cbr[1])
        elif(cbl[0]==None):
            return (cbr[0], cbl[1], cbr[1])
        return (cbl[0]+cbr[0]-1, cbl[1], cbr[1])

    def check_boat_up(self, row: int, col: int):
        """Verifica se ha pecas de barco para cima e, caso haja, se o barco termina """
        res = 1
        if(self.get_value(row, col) in ('t', 'T')):
            return(None, True)
        pos = self.get_value(row-res, col)
        while(res<4 and pos!='.' and pos!='w' and pos!='W'):
            res += 1
            pos = self.get_value(row-res, col)
        
        if(res < 2):
            return (None, False)
        return (res, self.get_value(row-res+1, col) == 't' or self.get_value(row-res+1, col) == 'T')
    
    def check_boat_down(self, row: int, col: int):
        """Verifica se ha pecas de barco para baixo e, caso haja, se o barco termina """
        res = 1
        if(self.get_value(row, col) in ('b', 'B')):
            return(None, True)
        pos = self.get_value(row+res, col)
        while(res<4 and pos!='.' and pos!='w' and pos!='W'):
            res += 1
            pos = self.get_value(row+res, col)

        if(res < 2):
            return (None, False)
        return (res, (self.get_value(row+res-1, col) == 'b' or self.get_value(row+res-1, col) == 'B'))
        
    def check_boat_vertical(self, row:int, col: int):
        """checks for a vertical boat and returns (size, ends_top?, ends_bottom?)"""
        cbu = self.check_boat_up(row, col)
        cbd = self.check_boat_down(row, col)
        if(cbu[0]==None and cbd[0]==None):
            return (None, False, False)
        elif(cbd[0]==None):
            return (cbu[0], cbu[1], cbd[1])
        elif(cbu[0]==None):
            return (cbd[0], cbu[1], cbd[1])
        return (cbu[0]+cbd[0]-1, cbu[1], cbd[1])
    
    def check_submarine(self, row: int, col: int):
        if(all(x == 'w' for x in (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col)))):
            self.board[row][col] = 'c'
            self.complete_boat(1)
    
    def put_water(self, row: int, col: int):
    
        if self.get_value(row, col) in ('w', 'W'):
            return 
            
        self.board[row][col] = 'w'
        self.empty_row_array[row] -= 1
        self.empty_col_array[col] -= 1
        adj_values = self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col)
    
        if(adj_values[0] == 'm'):
            aux = self.check_boat_left(row, col-1)
            if(aux[0] == None): #nao tem pecas de barco a esquerda
                self.check_submarine(row, col-1)
            elif(aux[1] == True): #barco encontrado termina
                self.complete_boat(aux[0])
                self.board[row][col-1] = 'r'
            else: #barco encontrado nao termina
                self.board[row][col-1] = 'r'
        if(adj_values[1] == 'm'):
            aux = self.check_boat_right(row, col+1)
            if(aux[0] == None): #nao tem pecas de barco a direita
                self.check_submarine(row, col+1)
            elif(aux[1] == True): #barco encontrado termina
                self.board[row][col+1] = 'l'
                self.complete_boat(aux[0])
            else: #barco encontrado nao termina
                self.board[row][col+1] = 'l'
        if(adj_values[2] == 'm'):
            aux = self.check_boat_up(row-1, col)
            if(aux[0] == None): #nao tem pecas de barco em cima
                self.check_submarine(row-1, col)
            elif(aux[1] == True): #barco encontrado termina
                self.board[row-1][col] = 'b'
                self.complete_boat(aux[0])
            else: #barco encontrado nao termina
                self.board[row-1][col] = 'b'
        if(adj_values[3] == 'm'):
            aux = self.check_boat_down(row+1, col)
            if(aux[0] == None): #nao tem pecas de barco em baixo
                self.check_submarine(row+1, col)
            elif(aux[1] == True): #barco encontrado termina
                self.board[row+1][col] = 't'
                self.complete_boat(aux[0])
            else: #barco encontrado nao termina
                self.board[row+1][col] = 't'
    
    def check_if_corner(self, row: int, col: int):
        """checks if a boat piece should be a corner, if so, it turns it into the respective one"""
        if(self.board[row][col] not in ('m', 'M')):
            return True
        adj_pos = (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col))

        cont = 0
        aux = 1
        for x in adj_pos:
            if(x not in ('w', 'W', '.') and adj_pos[cont+aux] in ('w', 'W')):
                pos_aux = ('r', 'l', 'b', 't')
                self.board[row][col] = pos_aux[cont]
                return True
            else:
                cont += 1
                aux *= -1
        return False

    def check_adj_corner(self, row: int, col: int):
        adj_pos = (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col))
        if adj_pos[0] == 'm' and self.get_value(row, col-2) in ('w', 'W'):
            self.board[row][col-1] = 'l'
        elif adj_pos[2] == 'm' and self.get_value(row-2, col) in ('w', 'W'):
            self.board[row-1][col] = 't'
        if adj_pos[1] == 'm' and self.get_value(row, col+2) in ('w', 'W'):
            self.board[row][col+1] = 'r'
        elif adj_pos[3] == 'm' and self.get_value(row+2, col) in ('w', 'W'):
            self.board[row+1][col] = 'b'
    
    def get_biggest_boat_size(self):
        """returns the biggest boat size"""
        boat_name = self.completed_boats
        if boat_name['couracado'] > 0:
            return 4
        elif boat_name['cruzadores'] > 0:
            return 3
        elif boat_name['contratorpedeiros'] > 0:
            return 2
        return 1
    
    def correct_boat_horiz(self, row: int, col: int, ends_left: bool, ends_right: bool):
        """corrects finished (horizontal)boat corners:
        recieves a pos(row, col) and 2 booleans to indicate if the boat ends in said directions"""
        pos = self.get_value(row, col)
        if not ends_left:
            cont = 0
            while pos in ('m', 'M', 'r'):
                cont += 1
                pos = self.get_value(row, col-cont)
            if self.get_value(row, col-cont+1) == 'm':
                self.board[row][col-cont+1] = 'l'
        pos = self.get_value(row, col)
        if not ends_right:
            cont = 0
            while pos in ('m', 'M', 'l'):
                cont += 1
                pos = self.get_value(row, col+cont)
            if self.get_value(row, col+cont-1) == 'm':
                self.board[row][col+cont-1] = 'r'
    
    def correct_boat_vert(self, row: int, col: int, ends_up: bool, ends_down: bool):
        """corrects finished (vertical)boat corners:
        recieves a pos(row, col) and 2 booleans to indicate if the boat ends in said directions"""
        pos = self.get_value(row, col)
        if not ends_up:
            cont = 0
            while pos in ('m', 'M', 'b'):
                cont += 1
                pos = self.get_value(row-cont, col)
            if self.get_value(row-cont+1, col) == 'm':
                self.board[row-cont+1][col] = 't'
        pos = self.get_value(row, col)
        if not ends_down:
            cont = 0
            while pos in ('m', 'M', 't'):
                cont += 1
                pos = self.get_value(row+cont, col)
            if self.get_value(row+cont-1, col) == 'm':
                self.board[row+cont-1][col] = 'b'
    
    def lookup_adj_M(self, row: int, col: int):
        adj_pos = (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col))
        if adj_pos[0] == 'M':
            self.put_boat_piece(row, col-2)
        elif adj_pos[1] == 'M':
            self.put_boat_piece(row, col+2)
        elif adj_pos[2] == 'M':
            self.put_boat_piece(row-2, col)
        elif adj_pos[3] == 'M':
            self.put_boat_piece(row+2, col)
    
    def check_completed_row(self, row: int):
        if self.row_array[row] == 0 and self.empty_row_array[row] > 0:
            for col in range(10):
                if self.get_value(row, col) == '.':
                    self.put_water(row, col)
    
    def check_completed_col(self, col: int):
        if self.col_array[col] == 0 and self.empty_col_array[col] > 0:
            for row in range(10):
                if self.get_value(row, col) == '.':
                    self.put_water(row, col)

    def put_boat_piece(self, row: int, col: int):
        if self.get_value(row, col) != '.':
            return
        
        #places water in corners
        corners = (self.get_value(row-1, col-1), self.get_value(row-1, col+1), self.get_value(row+1, col-1), self.get_value(row+1, col+1))
        if(corners[0]!='w' and corners[0]!='W'):
            self.put_water(row-1, col-1)
        if(corners[1]!='w' and corners[1]!='W'):
            self.put_water(row-1, col+1)
        if(corners[2]!='w' and corners[2]!='W'):
            self.put_water(row+1, col-1)
        if(corners[3]!='w' and corners[3]!='W'):
            self.put_water(row+1, col+1)
        
        #update row/col hint values
        self.row_array[row] -= 1
        self.col_array[col] -= 1
        self.empty_row_array[row] -= 1
        self.empty_col_array[col] -= 1

        self.board[row][col] = 'm'

        self.check_if_corner(row, col) #verifica se é um canto
        self.check_adj_corner(row, col) #verifica se os adjacentes passam a ser um canto

        horiz = self.check_boat_horizontal(row, col) #verifica se é um barco horizontal
        vert = self.check_boat_vertical(row, col) #verifica se é um barco vertical
        
        if(horiz[0]==vert[0] and vert[0]==None): #nao e barco vertical nem horizontal
            self.check_submarine(row, col)
        elif horiz[0] != None and horiz[1] and horiz[2]:
            self.complete_boat(horiz[0])
        elif vert[0] != None and vert[1] and vert[2]:
            self.complete_boat(vert[0])
        elif(horiz[0] != None and horiz[0] == self.get_biggest_boat_size()):
            self.complete_boat(horiz[0])
            self.correct_boat_horiz(row, col, horiz[1], horiz[2])
        elif(vert[0] != None and vert[0] == self.get_biggest_boat_size()):
            self.complete_boat(vert[0])
            self.correct_boat_vert(row, col, vert[1], vert[2])

        self.lookup_adj_M(row, col)
        self.check_completed_row(row)
        self.check_completed_col(col)
        
    def process_submarine(self, row: int, col:int):
        if all(pos in ('w', 'W', '.') for pos in (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col))):
            self.board[row][col] = 'c'
            self.complete_boat(1)

    def process_boat(self, size: int, boat_begin, boat_end, dir):
        if self.get_biggest_boat_size() == size:
            if boat_begin == boat_end:
                self.process_submarine(boat_begin[0], boat_begin[1])
                return
            pos_begin = self.get_value(boat_begin[0], boat_begin[1])
            pos_end = self.get_value(boat_end[0], boat_end[1])

            if pos_begin != 'm' and pos_end != 'm': # caso o barco ja esteja fechado dos dois lados
                return
            if pos_begin == 'm':
                self.board[boat_begin[0]][boat_begin[1]] = dir[0]
            if pos_end == 'm':
                self.board[boat_end[0]][boat_end[1]] = dir[1]
            self.complete_boat(size)
    
    def check_completed_boats_horizontal(self):
        for row in range(10):
            in_boat = False
            boat_size = 0
            for col in range(10):
                pos = self.get_value(row, col)
                if not in_boat and pos in ('l', 'L', 'm'):
                    in_boat = True
                    boat_size +=1
                    boat_begin = (row, col)
                elif in_boat:
                    if pos in ('m', 'M'):
                        boat_size += 1
                    elif pos in ('r', 'R'):
                        boat_end = (row, col)
                        boat_size += 1
                        self.process_boat(boat_size, boat_begin, boat_end, ('l', 'r'))
                        boat_size = 0
                        in_boat = False
                    elif pos in ('w', 'W', '.'):
                        boat_end = (row, col-1)
                        self.process_boat(boat_size, boat_begin, boat_end, ('l', 'r'))
                        boat_size = 0
                        in_boat = False
                        
    def check_completed_boats_vertical(self):
        for col in range(10):
            in_boat = False
            boat_size = 0
            for row in range(10):
                pos = self.get_value(row, col)
                if not in_boat and pos in ('t', 'T', 'm'):
                    in_boat = True
                    boat_size +=1
                    boat_begin = (row, col)
                elif in_boat:
                    if pos in ('m', 'M'):
                        boat_size += 1
                    elif pos in ('b', 'B'):
                        boat_end = (row, col)
                        boat_size += 1
                        self.process_boat(boat_size, boat_begin, boat_end, ('t', 'b'))
                        boat_size = 0
                        in_boat = False
                    elif pos in ('w', 'W', '.'):
                        boat_end = (row-1, col)
                        self.process_boat(boat_size, boat_begin, boat_end, ('t', 'b'))
                        boat_size = 0
                        in_boat = False
    
    def check_completed_boats(self):
        self.check_completed_boats_horizontal()
        self.check_completed_boats_vertical()
    
    def process_M(self, M):
        row = M[0]
        col = M[1]
        if self.row_array[row] >= 2 and self.col_array[col] >= 2: #tem espaco vertical e horizontal
            adj_values = (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col))
            if adj_values[0] in ('w', 'W') or adj_values[1] in ('w', 'W'):
                self.put_boat_piece(row-1, col)
                self.put_boat_piece(row+1, col)
                self.M_list.remove(M)
            elif adj_values[2] in ('w', 'W') or adj_values[3] in ('w', 'W'):
                self.put_boat_piece(row, col-1)
                self.put_boat_piece(row, col+1)
                self.M_list.remove(M)
        elif self.row_array[row] >= 2:
            self.put_boat_piece(row, col-1)
            self.put_boat_piece(row, col+1)
            self.M_list.remove(M)
        elif self.col_array[col] >= 2:
            self.put_boat_piece(row-1, col)
            self.put_boat_piece(row+1, col)
            self.M_list.remove(M)
        else:
            self.is_wrong = True
    
    def process_M_list(self):
        for M in self.M_list:
            self.process_M(M)
    
    def fill_trivial_lines(self):
        for i in range(10):
            if self.row_array[i] == self.empty_row_array[i]:
                for col in range(10):
                    if self.get_value(i, col) == '.':
                        self.put_boat_piece(i, col)
            if self.col_array[i] == self.empty_col_array[i]:
                for row in range(10):
                    if self.get_value(row, i) == '.':
                        self.put_boat_piece(row, i)
    
    def check_possible_boat_horiz(self, row: int, begin: int, end: int):
        if self.get_value(row, begin-1) not in ('w', 'W', '.') or self.get_value(row, end+1) not in ('w', 'W', '.') or self.get_value(row, begin) == 'M' or self.get_value(row, end) == 'M':
            return False, None
        for col in range(begin, end+1):
            adj_vert = self.adjacent_vertical_values(row, col)
            if adj_vert[0] not in ('w', 'W', '.') or adj_vert[1] not in ('w', 'W', '.'):
                return False, None
        return True, (row, begin, row, end)


    def search_fit_horiz(self, size: int):
        res = []
        for row in range(10):
            in_water = True
            current_size = 0
            for col in range(10):
                pos = self.get_value(row, col)
                if in_water and pos in ('l', 'L', 'm', '.'):
                    in_water = False
                    current_size += 1
                    b_begin = col
                elif not in_water:
                    if pos in ('m', 'M', 'r', 'R', '.'):
                        current_size += 1
                        if current_size == size:
                            b_end = col
                            current = self.check_possible_boat_horiz(row, b_begin, b_end)
                            if current[0]:
                                res.append(current[1])
                            current_size -= 1
                            b_begin += 1
                    else:
                        current_size = 0
        return res
    
    def check_possible_boat_vert(self, col: int, begin: int, end: int):
        if self.get_value(begin-1, col) not in ('w', 'W', '.') or self.get_value(end+1, col) not in ('w', 'W', '.') or self.get_value(begin, col) == 'M' or self.get_value(begin, col) == 'M':
            return False, None
        for row in range(begin, end+1):
            adj_horiz = self.adjacent_horizontal_values(row, col)
            if adj_horiz[0] not in ('w', 'W', '.') or adj_horiz[1] not in ('w', 'W', '.'):
                return False, None
        return True, (begin, col, end, col)
    
    def search_fit_vert(self, size: int):
        res = []
        for col in range(10):
            in_water = True
            current_size = 0
            for row in range(10):
                pos = self.get_value(row, col)
                if in_water and pos in ('t', 'T', 'm', '.'):
                    in_water = False
                    current_size += 1
                    b_begin = row
                elif not in_water:
                    if pos in ('m', 'M', 'b', 'B', '.'):
                        current_size += 1
                        if current_size == size:
                            b_end = row
                            current = self.check_possible_boat_vert(col, b_begin, b_end)
                            if current[0]:
                                res.append(current[1])
                            current_size -= 1
                            b_begin += 1
                    else:
                        current_size = 0
        return res

    
    def search_boat_size(self, size):
        return self.search_fit_horiz(size) + self.search_fit_vert(size)
    
      # TODO: outros metodos da classe        

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que pTodem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        if(all(x == 0 for x in self.board.completed_boats.values())):
            return True
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    board.print()
    # Imprimir valores adjacentes
    """print(board.get_value(0,0))
    print(board.adjacent_vertical_values(3, 3))
    print(board.adjacent_horizontal_values(3, 3))
    print(board.adjacent_vertical_values(1, 0))
    print(board.adjacent_horizontal_values(1, 0))
    print(board.adjacent_vertical_values(8, 8))
    """
    print(board.completed_boats) #barcos que faltam completar (por tipo de barco)
    print(board.row_array, board.col_array) #pistas das linhas e colunas
    print(board.get_biggest_boat_size())

    """teste de put_water"""
    """board.board[7][8] = 'm'
    board.board[6][8] = 'm'
    board.put_water(5, 8)

    board.print()
    print(board.completed_boats)"""

    """teste de put_boat_piece"""
    """board.put_water(6, 8)
    board.put_boat_piece(5, 8)
    board.put_water(3, 8)
    board.put_boat_piece(4, 8)
    print(board.board[4][7], board.board[4][9], board.board[6][7], board.board[6][9])
    print(board.row_array, board.col_array)
    board.print()
    print(board.completed_boats)"""

    """teste de put_boat_piece -> correct boat (necessario desligar o put water do parse para funcionar)"""
    """board.put_boat_piece(6, 8)
    board.put_boat_piece(5, 8)
    board.put_boat_piece(2, 0)
    board.put_boat_piece(1, 5)
    board.put_boat_piece(1, 7)
    board.print()
    print(board.completed_boats)"""

    """teste de check_completed_boats: com barcos identicos ao teste de cima mas por ordem diferente de adicao"""
    """board.put_boat_piece(2, 0)
    board.put_boat_piece(1, 5)
    board.put_boat_piece(1, 7)
    board.put_boat_piece(6, 8)
    board.put_boat_piece(5, 8)
    board.check_completed_boats()
    board.print()
    print(board.completed_boats)"""

    """teste de process_submarine: com instancia identica ao teste de cima"""
    """board.put_boat_piece(2, 0)
    board.put_boat_piece(1, 5)
    board.put_boat_piece(1, 7)
    board.put_boat_piece(5, 2)
    board.put_boat_piece(6, 2)
    board.put_boat_piece(8, 2)
    board.put_boat_piece(9, 2)
    board.put_boat_piece(5, 4)
    board.put_boat_piece(6, 4)
    board.put_boat_piece(5, 6)
    board.put_boat_piece(6, 8)
    board.put_boat_piece(5, 8)
    board.check_completed_boats()
    board.print()
    print(board.completed_boats)"""

    """teste de process_M_list"""
    """board.process_M_list()
    board.fill_trivial_lines()
    board.fill_trivial_lines()
    board.print()
    print(board.completed_boats)
    print(board.row_array, board.col_array)"""

    """teste de search_boats_size"""
    """print(board.search_boat_size(4))"""

    """teste de check_boats
    board.board[7][8] = 'm'
    board.board[6][8] = 'm'
    board.board[5][8] = 'm'
    board.print()
    board.put_water(4, 8)
    print("+++++++++++++++++")
    board.print()
    print(board.check_boat_vertical(6, 8))
    print(board.check_boat_vertical(5, 8))"""

    #bimaru = Bimaru(board)
    #solution = astar_search(bimaru)
    #print(solution.solution())
    #print(solution.path_cost)
    #print(solution)
    
    
"""verificacao de boat piece ter tamanho do maior barco possivel -> completa barco
maybe fazer um check_uncompleted_boats(size) que ao completar um barco de tamanho k (sendo esse o ultimo desse tamanho)
    verifica se existe algum de tamanho k-1 incompleto (que passa a ser consideradp completo)
    Exº:    Imaginando se que se                entao
    completa um destes barcos de 3              --->
    ..........                      ..........          ..........
    .mmm......                      .mmm......          .rml......
    ..........                      ..........          ..........
    ..........                      ..........          ..........
    ....m.....                      ....m.....          ....t.....
    ....m.....                      ....m.....          ....m.....
    ....m.....                      ....m.....          ....b.....
    ..........                      ..........          ..........
    ......mmm.                      .....rmml.          .....rmml.
    ..........                      ..........          ..........

^esta funcao devera ser uma das actions isolada que percorre o tabuleiro em busca de barcos completos em tamanho mas nao em formato
que percorre um barco e transforma as pontas em cantos de barco (l,r,t,b)
ou entao fazer com que o check boat devolva as posicoes das pontas ou que ao percorrer o barco complete as pontas

(done)put_boat_piece: se houver um M adjacente: tentar preencher do outro lado do M

(done)put_boat_piece: se ao meter uma peca de barco se completa uma linha ou uma coluna: preencher o resto de agua

(done)fazer funcao que itera por todas as linhas e colunas observando se o numero de posicoes por preencher corresponde ao
numero de posicoes de barco que ainda faltam nessa row/col e, se tal se verificar, preencher a row/col de pedacos de
barco

(done)put_boat_piece: ao completar o barco verificar se isso completa os barcos desse tamanho -> barcos de tamanho inferior podem
ficar completos por consequencia

(done? -> feito por consequencia dos pieces colocados anteriormente) check_corner: se se torna num corner -> meter agua nos adjacentes necessarios

(done)fazer funcao que procura sitios possiveis para o barco de maior tamanho possivel"""