from table import table
from point import point
from copy import copy
import log
import curses
import sys
import os

MoveChars = list(map(ord, list("hjkl")))
ChangeActiveTableChars = [curses.KEY_SF, curses.KEY_SR]
ChangeActiveCellChars = list(map(ord, list("[{}]")))
ShortCutChars = [ord('y'), ord('Y')]
KeyBindings = {}

class page:
    def __init__(self, screen):
        self.tables = []
        self.tables_movements = []
        self.current_shift = point()
        self.active_table = -1
        self.screen = screen
        self.display_size = point()

    def redraw(self):
        for i in range(len(self.tables)):
            self.tables[i].redraw(self.screen, self.tables_movements[i])
        if (self.active_table != -1):
            self.tables[self.active_table].draw_active_cell(self.screen,
                                        self.tables_movements[self.active_table])

    def add_table(self, table):
        self.tables.append(table)
        if (len(self.tables_movements) == 0):
            self.tables_movements.append(point())
        else:
            self.tables_movements.append(self.tables_movements[-1]
                                        + point(self.tables[-1].height))

    def refresh(self, size):
        self.screen.refresh(self.current_shift.x, self.current_shift.y,
                            0, 0, size.x - 1, size.y - 1)
        self.display_size = copy(size)
    
    def onScreen(self, cell):
        xOnScreen = self.current_shift.x <= cell.x and \
                    cell.x < (self.current_shift.x + self.display_size.x)
        yOnScreen = self.current_shift.y <= cell.y and \
                    cell.y < (self.current_shift.y + self.display_size.y)
        return xOnScreen and yOnScreen;


    def move_to_active(self):
        if (self.active_table != -1):
            if not self.onScreen(self.tables_movements[self.active_table] +\
                                 self.tables[self.active_table].active_cell_point()):
                self.current_shift = self.tables_movements[self.active_table] +\
                point(self.tables[self.active_table].active_cell_point().x)
                log.DebugLog << self.current_shift
        self.refresh(self.display_size)

    def move(self, c):
        if (c == curses.KEY_UP or c == 'j'):
            self.current_shift.x -= 1
        elif (c == curses.KEY_DOWN):
            self.current_shift.x += 1
        elif (c == 'h'):
            self.current_shift.y -= 1
        elif (c == 'l'):
            self.current_shift.y += 1
        self.current_shift.x = max(0, self.current_shift.x)
        self.current_shift.y = max(0, self.current_shift.y)

    def changeActiveTable(self, c):
        self.tables[self.active_table].active_cell = -1
        self.tables[self.active_table].redraw(self.screen,
                                        self.tables_movements[self.active_table])
        if (c == curses.KEY_SR):
            self.active_table -= 1
        elif (c == curses.KEY_SF):
            self.active_table += 1
        self.active_table %= len(self.tables)
        self.tables[self.active_table].active_cell = 0
        self.tables[self.active_table].redraw(self.screen,
                                        self.tables_movements[self.active_table])
        self.move_to_active()

    def changeActiveCell(self, c):
        c = chr(c)
        if (c == '['):
            self.tables[self.active_table].prev_column()
        elif (c == ']'):
            self.tables[self.active_table].next_column()
        elif (c == '{'):
            self.tables[self.active_table].prev_row()
        elif (c == '}'):
            self.tables[self.active_table].next_row()
        self.tables[self.active_table].redraw(self.screen,
                                        self.tables_movements[self.active_table])
        
    def executeShortcut(self, c):
        c = chr(c)
        if (c == 'y'):
            if (self.active_table != -1):
                file = open("/tmp/email-tui-buffer", "w")
                file.write(self.tables[self.active_table].get_row_data() + '\n')
                file.close()
                os.system("xclip -i /tmp/email-tui-buffer")
        elif c == 'Y':
            if (self.active_table != -1):
                file = open("/tmp/email-tui-buffer", "w")
                file.write('\n'.join(self.tables[self.active_table].get_formatted_data()) + '\n')
                file.close()
                os.system("xclip -i /tmp/email-tui-buffer")

    def callback_char(self, c):
        if (c in MoveChars):
            self.move(c)
        elif c in ChangeActiveTableChars:
            self.changeActiveTable(c)
        elif c in ChangeActiveCellChars:
            self.changeActiveCell(c)
        elif c in ShortCutChars:
            self.executeShortcut(c)

