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
        if(v1=='.'):
            v1 = None
        if(v2=='.'):
            v2 = None
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
        if(v1=='.'):
            v1 = None
        if(v2=='.'):
            v2 = None
        return v1, v2
        
    def print(self):
        for i in self.board:
            for j in i:
                if (j == 'w'):
                    print('.', end = '')
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
        num_hints = int(lines[2][0])

        for i in range(3, 3 + num_hints):
            row = int(lines[i][1])
            col = int(lines[i][2])
            value = lines[i][3]
            board.board[row][col] = value #atualiza o boardgame com as hints iniciais
            board.row_array[row] -= 1 #atualiza o numero de pecas de barco que ainda faltam marcar na linha
            board.col_array[col] -= 1 #atualiza o numero de pecas de barco que ainda faltam marcar na coluna
            if value == 'C':
                board.completed_boats['submarines'] -= 1
        
        return board
    
    def complete_boat(self, size: int):
        if size == 1:
            self.completed_boats['submarine'] -= 1
        elif size == 2:
            self.completed_boats['contratorpedeiros'] -= 1
        elif size == 3:
            self.completed_boats['cruzadores'] -= 1
        else:
            self.completed_boats['couracado'] -= 1
    
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
        """checks for an horizontal boat and returns (size, ends_left?, ends_right?)"""
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
        if(all(x == 'w' for x in (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values))):
            self.board[row][col] = 'c'
        self.complete_boat(1)
    
    def put_water(self, row: int, col: int):
        self.board[row][col] = 'w'
        adj_values = board.adjacent_horizontal_values(row, col) + board.adjacent_vertical_values(row, col)

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
        if(self.board[row][col] in ('r', 'R', 'l', 'L', 't', 'T', 'b', 'T')):
            return True
        adj_pos = (self.adjacent_horizontal_values(row, col) + self.adjacent_vertical_values(row, col))

        cont = 0
        for x in adj_pos:
            if(x == 'w' or x == 'W'):
                cont += 1
            else:
                aux = cont
                break
        if(cont == 3 and adj_pos[aux] != '.'):
            pos_aux = ('r', 'l', 'b', 't')
            self.board[row][col] = pos_aux[aux]
            return True
        elif(cont == 3 and adj_pos[aux] == 'c'):
            pos_aux1 = ()
            self.check_if_corner()
        return False
    
    def put_boat_piece(self, row: int, col: int):
        corners = (self.get_value(row-1, col-1), self.get_value(row-1, col+1), self.get_value(row+1, col-1), self.get_value(row+1, col+1))
        if(corners[0]!='w' and corners[0]!='W'):
            self.put_water(row-1, col-1)
        if(corners[1]!='w' and corners[1]!='W'):
            self.put_water(row-1, col+1)
        if(corners[2]!='w' and corners[2]!='W'):
            self.put_water(row+1, col-1)
        if(corners[3]!='w' and corners[3]!='W'):
            self.put_water(row+1, col+1)
        
        self.row_array[row] -= 1
        self.col_array[col] -= 1

        self.check_if_corner(row, col)
        self.check_adj_corner(row, col)

        horiz = self.check_boat_horizontal(row, col)
        vert = self.check_boat_vertical(row, col)
        
        if(horiz[0]==vert[0] and vert[0]==None):
            self.check_submarine(row, col)

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
    print(board.get_value(0,0))
    print(board.adjacent_vertical_values(3, 3))
    print(board.adjacent_horizontal_values(3, 3))
    print(board.adjacent_vertical_values(1, 0))
    print(board.adjacent_horizontal_values(1, 0))
    print(board.adjacent_vertical_values(8, 8))
    print(board.completed_boats) #barcos que faltam completar (por tipo de barco)
    print(board.row_array, board.col_array) #pistas das linhas e colunas

    """teste de put_water"""
    """board.board[7][8] = 'm'
    board.board[6][8] = 'm'
    board.put_water(5, 8)

    board.print()
    print(board.completed_boats)"""

    """teste de put_boat_piece"""
    """board.put_boat_piece(5, 8)
    print(board.board[4][7], board.board[4][9], board.board[6][7], board.board[6][9])
    print(board.row_array, board.col_array)"""

    """teste de check_boats"""
    """board.board[7][8] = 'm'
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
    
    
"""falta check_new_corners"""