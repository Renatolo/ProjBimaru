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
        #dicionario com os barcos que ja estao completps
        self.completed_boats = {"couracado": 0, "cruzadores": 0, "contraturpedos": 0, "submarines": 0}
        
    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        #falta aqui a questão de ter de devolver None se os pontos estiverem fora da grelha
        v1 = self.board[row-1][col]
        v2 = self.board[row+1][col]
        if(v1=='.' or row<1):
            v1 = None;
        if(v2=='.' or row>8):
            v2 = None;
        return v1, v2

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        v1 = self.board[row][col-1]
        v2 = self.board[row][col +1]
        if(v1 == '.' or col < 1):
            v1 = None;
        if(v2 == '.' or col > 8):
            v2 = None
        return v1, v2
        
    def print(self):
        for i in self.board:
            for j in i:
                print(j, end="")
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
        
        board.row_array = lines[0][1:] #row hints array
        board.col_array = lines[1][1:] #column hints array
        num_hints = int(lines[2][0])
        for i in range(3, 3 + num_hints):
            row = int(lines[i][1])
            col = int(lines[i][2])
            value = lines[i][3]
            board.board[row][col] = value
        
        return board
        
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
    print(board.completed_boats)
    print(board.row_array, board.col_array)

    #bimaru = Bimaru(board)
    #solution = astar_search(bimaru)
    #print(solution.solution())
    #print(solution.path_cost)
    #print(solution)
    
    
