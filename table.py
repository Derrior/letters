import os
from copy import copy
from point import point
import curses


log = open("log.txt", "w")

def compress_word(word, width):
    if width < 3:
        return "." * width
    return word[:(width - 3) * 2 // 3] + "↞ ↠" + word[-(width - 3) // 3:]


def parse_line(result, words, width):
    result.append("")
    for i in range(len(words)):
        if (len(result[-1]) > 0 and len(result[-1]) + len(words[i]) + 1 <= width):
            result[-1] += ' ' + words[i]
        else:
            if (len(result[-1]) == 0):
                result.pop()
            else:
                result[-1] = result[-1].center(width, ' ')
            if (len(words[i]) <= width):
                result.append(words[i])
            else:
                result.append(compress_word(words[i], width))
    result[-1] = result[-1].center(width, ' ')


def get_content(string, width, max_line_width):
    result = []
    lines = string.split('\n')
    for j in range(len(lines)):
        words = lines[j].split(' ')
        parse_line(result, words, width)
    if (max_line_width > 1):
        if (len(result) > max_line_width):
            result = result[:max_line_width - 2] + ['~' * width] + result[-1:]
    return result


def get_content_line(content_block, index):
    if (index < len(content_block)):
        return content_block[index]
    return ' ' * len(content_block[0])


def decrease_width_if_possible(width, terminal_width):
    current_column = 0
    while (sum(width) > terminal_width - len(width) - 1):
        width[current_column] -= 1
        current_column += 1
        current_column %= len(width)

def increase_width_if_possible(width, terminal_width):
    current_column = 0
    while (sum(width) < terminal_width - len(width) - 1):
        width[current_column] += 1
        current_column += 1
        current_column %= len(width)

def get_table_columns_width(width, terminal_columns):
    koeff = 1
    while (sum(width) * (koeff + 1) <= terminal_columns - len(width) - 1):
        koeff += 1
    table_columns_width = [width[i] * koeff for i in range(len(width))]
    
    current_column = 0
    decrease_width_if_possible(table_columns_width, terminal_columns)
    increase_width_if_possible(table_columns_width, terminal_columns)
    return table_columns_width
    

def separator_line(width):
    output = []
    output.append('+')
    for j in range(len(width)):
        output.append('-' * width[j] + '+')
    output.append('\n')
    return ''.join(output)
    

def make_table(arr, width=0, max_line_width = -1):
    if (width == 0):
        width = [1] * len(arr[0])
    columns, lines = os.get_terminal_size()
    table_contents = [[0] * len(arr[0]) for i in range(len(arr))]
    table_columns_width = get_table_columns_width(width, columns)

    for i in range(len(arr)):
        for j in range(len(arr[0])):
            table_contents[i][j] = get_content(arr[i][j], table_columns_width[j], max_line_width)
    return table_contents, table_columns_width



class table:
    def __init__(self, arr):
        self.resource = arr
        self.content, self.column_width = make_table(arr)
        self.row_amount, self.column_amount = len(self.content), len(self.content[0])
        self.row_width = [0] * self.row_amount
        self.row_data = self.rows()
        self.height, self.width = len(self.row_data), len(self.row_data[0])
        self.active_cell = -1

    def next_column(self):
        self.active_cell += 1
        self.active_cell %= self.row_amount * self.column_amount

    def prev_column(self):
        self.active_cell -= 1
        self.active_cell %= self.row_amount * self.column_amount

    def next_row(self):
        self.active_cell += self.column_amount
        self.active_cell %= self.row_amount * self.column_amount
        
    def prev_row(self):
        self.active_cell -= self.column_amount
        self.active_cell %= self.row_amount * self.column_amount

    def get_row_data(self, cell_idx = -2):
        if (cell_idx == -2):
            cell_idx = self.active_cell
        if (cell_idx == -1):
            return ""
        return self.resource[cell_idx // self.column_amount][cell_idx % self.column_amount]

    def rows(self):
        output = ['\n']
        separator = separator_line(self.column_width)
        output.append(separator)
        for i in range(self.row_amount):
            line_height = max([len(self.content[i][j]) for j in range(self.column_amount)])
            self.row_width[i] = line_height
            for line_index in range(line_height):
                for j in range(self.column_amount):
                    output.append('|' + get_content_line(self.content[i][j], line_index))
                output.append('|\n')
                output.append(separator)
        return ''.join(output).split('\n')

    
    def active_row(self):
        return self.active_cell // self.column_amount

    def active_column(self):
        return self.active_cell % self.column_amount

    def active_cell_point(self):
        row, column = self.active_row(), self.active_column()
        return point(sum(self.row_width[:row]), sum(self.column_width[:column]))

    def redraw(self, screen, movement):
        output = self.row_data
        for i in range(len(output)):
            screen.addstr(i + movement.x, movement.y, output[i])
        if (self.active_cell != -1):
            x_shift = sum(self.column_width[:self.active_column()]) + self.active_column() + 1
            y_shift = sum(self.row_width[:self.active_row()]) + self.active_row() + 1
            for i in range(1, self.row_width[self.active_row()] + 1):
                screen.chgat(y_shift + i + movement.x, x_shift,
                            self.column_width[self.active_column()], curses.A_BOLD)


    def resize(self, screen, movement):
        self.content, self.column_width = make_table(self.arr)
        self.row_amount, self.column_amount = len(self.content), len(self.content[0])
        self.row_data = self.rows()
        self.height, self.width = len(self.row_data), len(self.row_data[0])
