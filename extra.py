FPS = 30
WINDOW_SIZE = (900, 700)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CELL_COUNT = 8
CELL_SIZE = 70
COLOURS = ['black square.jpg', 'white square.png']
names = 'ABCDEFGH'
DIRECTIONS = {'A': ['B'],
              'B': ['A', 'C'],
              'C': ['B', 'D'],
              'D': ['C', 'E'],
              'E': ['D', 'F'],
              'F': ['E', 'G'],
              'G': ['F', 'H'],
              'H': ['G']
              }

QUEEN_DIRECTIONS = {'A': [['B'], ['C'], ['D'], ['E'], ['F'], ['G'], ['H']],
                    'B': [['A', 'C'], ['D'], ['E'], ['F'], ['G'], ['H']],
                    'C': [['B', 'D'], ['A', 'E'], ['F'], ['G'], ['H']],
                    'D': [['C', 'E'], ['B', 'F'], ['A', 'G'], ['H']],
                    'E': [['D', 'F'], ['C', 'G'], ['B', 'H'], ['A']],
                    'F': [['E', 'G'], ['D', 'H'], ['C'], ['B'], ['A']],
                    'G': [['F', 'H'], ['E'], ['D'], ['C'], ['B'], ['A']],
                    'H': [['G'], ['F'], ['E'], ['D'], ['C'], ['B'], ['A']]
                    }

HIT_DIRECTIONS = {'A': {'B': 'C'},
                  'B': {'C': 'D'},
                  'C': {'B': 'A', 'D': 'E'},
                  'D': {'C': 'B', 'E': 'F'},
                  'E': {'D': 'C', 'F': 'G'},
                  'F': {'E': 'D', 'G': 'H'},
                  'G': {'F': 'E'},
                  'H': {'G': 'F'}
                  }
WHITE_QUEEN_FIELD = {'B8', 'D8', 'F8', 'H8'}
BLACK_QUEEN_FIELD = {'A1', 'C1', 'E1', 'G1'}
types = {
    'ch': ('Checker2', 'b'), 'CH': ('Checker1', 'w'),
    'q': ('Queen2', 'b'), 'Q': ('Queen1', 'w'),
}
