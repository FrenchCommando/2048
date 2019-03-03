import random
import tkinter as tk
import tkinter.font


class Board:
    def __init__(self, x=4, y=4, p=0.9):
        self.x = x
        self.y = y
        self.p = p
        self.board_d = {}
        self.last_d = Direction.DOWN
        self.next_available_indexes = [0 for u in range(max(self.x, self.y))]
        self.board = [[0 for j in range(self.y)] for i in range(self.x)]
        self.add()

    def describe_dimension(self, d):
        x, y = (self.x, self.y) if d in ["UP", "DOWN"] else (self.y, self.x)
        if d == "UP":
            def way(i, j):
                return i, y - j - 1
        elif d == "DOWN":
            def way(i, j):
                return i, j
        elif d == "LEFT":
            def way(i, j):
                return j, i
        elif d == "RIGHT":
            def way(i, j):
                return y - j - 1, i
        else:
            def way(i, j):
                return -1, -1
            # should throw something here
        return x, y, way

    def add(self):
        x, y, z = self.describe_dimension(self.last_d)
        n = sum([y - self.next_available_indexes[k] for k in range(x)])
        # n can't be zero because I just moved
        r = random.randint(1, n) - 1
        i = 0
        available = y - self.next_available_indexes[i]
        while r >= available:
            r -= available
            i += 1
            available = y - self.next_available_indexes[i]
        p = random.random()
        value = 2 if p < self.p else 4
        xx, yy = z(i, r + self.next_available_indexes[i])
        self.board_d[xx, yy] = value
        self.board[xx][yy] = value

    def single_shift(self, d, i):
        ref_x, ref_y, ref_z = self.describe_dimension(d)
        value = 0
        values = []
        last_index = -1
        for y in range(ref_y):
            ii, jj = ref_z(i, y)
            v = self.board[ii][jj]
            if v == 0:
                continue
            if v == value:
                value = 0
                values[-1] += v
            else:
                value = v
                values.append(v)
            last_index = y + 1
        self.next_available_indexes[i] = len(values)
        if last_index == len(values):
            return False
        for y, v in enumerate(values):
            ii, jj = ref_z(i, y)
            self.board_d[ii, jj] = v
            self.board[ii][jj] = v
        for y in range(len(values), last_index):
            ii, jj = ref_z(i, y)
            self.board_d[ii, jj] = 0
            self.board[ii][jj] = 0
        return True

    def shift(self, d):
        r = self.x if d in [Direction.UP, Direction.DOWN] else self.y
        return any([self.single_shift(d, i) for i in range(r)])

    def move(self, d):
        self.last_d = d
        moved = self.shift(d)
        if moved:
            self.add()
        return moved

    def get_score(self):
        return sum(self.board_d.values())

    def restart(self):
        pass

    def terminate(self):
        pass


class Direction:
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    keycode_mapping = {
        113: LEFT,
        114: RIGHT,
        116: DOWN,
        111: UP,
        38: LEFT,  # qwerty
        40: RIGHT,
        39: DOWN,
        25: UP,
    }

    @staticmethod
    def from_keycode(keycode):
        return Direction.keycode_mapping[keycode]


class GameDisplay(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.minsize(width=300, height=50)
        self.pack()

        self.hi_there = None
        self.game = None
        self.table = None
        self.score = None
        self.button_table = None
        self.quit = None

        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self, text="New Game\n(click me)",
                                  fg="blue", command=self.start_game)
        self.hi_there.pack(side="top")
        self.quit = tk.Button(self, text="CLOSE", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def start_game(self):
        self.hi_there.config(text="NewGame")
        if self.table is not None:
            self.table.destroy()
        if self.game is not None:
            self.game.terminate()
        if self.score is not None:
            self.score.destroy()
        x, y, p = 4, 4, 0.9
        d = dict(x=x, y=y, p=p)
        self.game = Board(**d)
        self.score = tk.Label(self.master, text="Score\t0")
        self.score.pack()
        self.table = tk.Frame(self.master)

        text_font = tk.font.Font(family='Helvetica', size=20, weight='bold')

        def build_button(col, row):
            button = tk.Button(self.table, text="%s,%s" % (row, col), height=1, width=2,
                               bg='red', font=text_font)
            button.grid(row=row, column=col, sticky="nsew")
            return button

        self.button_table = [[build_button(i, y - j - 1) for j in range(y)] for i in range(x)]
        self.table.pack()
        self.bind_all('<Key>', self.update_game)

    def update_game(self, event):
        # if event.char == event.keysym:
        #     msg = 'Normal Key %r' % event.char
        # elif len(event.char) == 1:
        #     msg = 'Punctuation Key %r (%r)' % (event.keysym, event.char)
        # else:
        #     msg = 'Special Key %r' % event.keysym
        # print(msg)
        d = Direction.from_keycode(event.keycode)
        # print(event.keysym, event.keycode, d.__repr__())
        self.game.move(d)
        self.update_display()

    color_mapping = {
        0: 'red',
        2: 'orange',
        4: 'green',
        8: 'blue',
        16: 'yellow',
        32: 'purple',
        64: 'cyan',
        128: 'magenta'
    }

    def update_display(self):
        for i in range(self.game.x):
            for j in range(self.game.y):
                val = self.game.board[i][j]
                s_val = str(val) if val != 0 else ""
                self.button_table[i][j].config(text=s_val, bg=self.color_mapping.get(val, 'white'))
                if len(s_val) >= 2:
                    text_font = tk.font.Font(family='Helvetica', size=10, weight='bold')
                else:
                    text_font = tk.font.Font(family='Helvetica', size=20, weight='bold')
                self.button_table[i][j].config(font=text_font)
        self.score.config(text="Score: {}".format(str(self.game.get_score())))


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game 2048')
    root.attributes('-topmost', True)
    app = GameDisplay(master=root)
    app.mainloop()
