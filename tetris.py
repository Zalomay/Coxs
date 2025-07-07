import curses
import random
import time

# Game configuration
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TICK_RATE = 0.3  # time between automatic falls

# Tetromino shapes and colors
SHAPES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'J': [
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[0, 1], [0, 1], [1, 1]]
    ],
    'L': [
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]]
    ]
}

COLORS = {
    'I': curses.COLOR_CYAN,
    'J': curses.COLOR_BLUE,
    'L': curses.COLOR_YELLOW,
    'O': curses.COLOR_MAGENTA,
    'S': curses.COLOR_GREEN,
    'T': curses.COLOR_RED,
    'Z': curses.COLOR_WHITE
}


def rotate(shape, rotation):
    """Return rotated shape."""
    states = SHAPES[shape]
    return states[rotation % len(states)]


def new_piece():
    shape = random.choice(list(SHAPES.keys()))
    rotation = 0
    piece = rotate(shape, rotation)
    x = BOARD_WIDTH // 2 - len(piece[0]) // 2
    y = 0
    return {'shape': shape, 'rotation': rotation, 'cells': piece, 'x': x, 'y': y}


def check_collision(board, piece, dx=0, dy=0, rotation=None):
    if rotation is None:
        rotation = piece['rotation']
    cells = rotate(piece['shape'], rotation)
    for cy, row in enumerate(cells):
        for cx, val in enumerate(row):
            if not val:
                continue
            x = piece['x'] + cx + dx
            y = piece['y'] + cy + dy
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return True
            if y >= 0 and board[y][x] != ' ':
                return True
    return False


def merge_piece(board, piece):
    cells = rotate(piece['shape'], piece['rotation'])
    for cy, row in enumerate(cells):
        for cx, val in enumerate(row):
            if val:
                x = piece['x'] + cx
                y = piece['y'] + cy
                if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
                    board[y][x] = piece['shape']


def clear_lines(board):
    new_board = [row for row in board if any(cell == ' ' for cell in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [' '] * BOARD_WIDTH)
    return new_board, cleared


def draw_board(stdscr, board, piece, score):
    stdscr.clear()
    # draw borders
    stdscr.border()
    # draw board
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            char = ' '
            color = 0
            if cell != ' ':
                char = '[]'
                color = COLORS[cell]
            stdscr.addstr(y + 1, x * 2 + 1, char, curses.color_pair(color))
    # draw piece
    cells = rotate(piece['shape'], piece['rotation'])
    for cy, prow in enumerate(cells):
        for cx, val in enumerate(prow):
            if val:
                px = piece['x'] + cx
                py = piece['y'] + cy
                if py >= 0:
                    stdscr.addstr(py + 1, px * 2 + 1, '[]', curses.color_pair(COLORS[piece['shape']]))
    stdscr.addstr(0, BOARD_WIDTH * 2 + 3, f"Score: {score}")
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    # init colors
    curses.start_color()
    for idx, color in COLORS.items():
        curses.init_pair(color, color, color)

    board = [[' '] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
    piece = new_piece()
    score = 0
    last_fall = time.time()

    while True:
        draw_board(stdscr, board, piece, score)
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_LEFT and not check_collision(board, piece, dx=-1):
            piece['x'] -= 1
        elif key == curses.KEY_RIGHT and not check_collision(board, piece, dx=1):
            piece['x'] += 1
        elif key == curses.KEY_DOWN and not check_collision(board, piece, dy=1):
            piece['y'] += 1
        elif key == curses.KEY_UP:
            new_rot = piece['rotation'] + 1
            if not check_collision(board, piece, rotation=new_rot):
                piece['rotation'] = new_rot
                piece['cells'] = rotate(piece['shape'], piece['rotation'])

        now = time.time()
        if now - last_fall > TICK_RATE:
            if check_collision(board, piece, dy=1):
                merge_piece(board, piece)
                board, cleared = clear_lines(board)
                score += cleared * 100
                piece = new_piece()
                if check_collision(board, piece):
                    break  # game over
            else:
                piece['y'] += 1
            last_fall = now

    stdscr.nodelay(False)
    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH - 4, 'Game Over')
    stdscr.addstr(BOARD_HEIGHT // 2 + 1, BOARD_WIDTH - 4, f'Score: {score}')
    stdscr.refresh()
    stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)
