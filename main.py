import curses
import log
from time import sleep
from page import page
from copy import copy
from point import point
import table

def mainloop(screen, page):
    current_cell = [0, 0]
    while True:
        c = screen.getch()
        if (c == ord('q') or c == 'q'):
            break
        if c == -1:
            continue
        page.callback_char(c)
        curses.update_lines_cols()
        page.refresh(point(curses.LINES, curses.COLS))

def main(screen):
    screen.clear()
    screen = curses.newpad(500, 500)
    curses.cbreak()
    screen.nodelay(True)
    screen.keypad(True)
    curses.curs_set(0)
    main_page = page(screen)
    for j in range(1, 10):
        arr = [[0] * 5 for i in range(3)]
        for i in range(5):
            v = i + j
            arr[0][i] = '1000 divided by {} is {}'.format(v, 1000 / v)
        for i in range(5):
            v = i + j + 10
            arr[1][i] = '1000 divided by {} is {}'.format(v, 1000 / v)
        for i in range(5):
            v = i + j + 15
            arr[2][i] = '1000 divided by {} is {}'.format(v, 1000 / v)
        new_arr = [[arr[j][i] for j in range(3)] for i in range(5)]
        Table = table.table(new_arr)
        main_page.add_table(Table)
    main_page.redraw()
    main_page.refresh(point(curses.LINES, curses.COLS))
    mainloop(screen, main_page)


log.MinLogLevel = log.DEBUG
curses.wrapper(main)

    
