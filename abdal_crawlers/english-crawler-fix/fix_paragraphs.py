import os
from enum import Enum, auto
from os import listdir
from os.path import isfile, join
import pandas as pd


class Type(Enum):
    MID_LINE = auto()
    END_LINE = auto()


raw_addr = "./UK-full/"
fixed_addr = "./UK-full-fixed/"
MAX_LINE_SIZE = 80
fixed_files_list = 'fixed_list.csv'


def add_to_csv(name: str):
    df = pd.DataFrame({'name': [name]})
    df.to_csv(fixed_files_list, mode='a', encoding="utf-16", header=not os.path.exists(fixed_files_list))


def need_fix(lines: list):
    # for line in lines:
    #     if len(line.strip()) > MAX_LINE_SIZE + 10:
    #         return False
    return True


def first_word_in_line_len(line: str):
    return len(line.split(" ")[0])


def detect_lines_type(lines: list):
    types = {}
    for index in range(len(lines)):
        if index + 1 < len(lines) and \
                len(lines[index]) < MAX_LINE_SIZE <= len(lines[index]) + first_word_in_line_len(lines[index + 1]) + 1:
            types[index] = Type.MID_LINE
        else:
            types[index] = Type.END_LINE
    types[len(lines)] = Type.END_LINE
    return types


def run():
    files = [f for f in listdir(raw_addr) if isfile(join(raw_addr, f))]
    for file_addr in files:
        _file = open(raw_addr + file_addr, 'r', encoding="utf-8")
        lines = _file.readlines()
        lines = [line for line in lines if len(line.strip()) != 0]
        _file.close()
        if not need_fix(lines):
            _file = open(fixed_addr + file_addr, 'w', encoding="utf-8")
            _file.writelines(lines)
            _file.close()
            continue
        types = detect_lines_type(lines)
        fixed = ""
        for index in range(len(lines)):
            if types[index] == Type.MID_LINE:
                fixed += lines[index].replace("\n", " ")
            else:
                fixed += lines[index]

        _file = open(fixed_addr + file_addr, 'w', encoding="utf-8")
        _file.write(fixed)
        _file.close()
        add_to_csv(file_addr)


if __name__ == '__main__':
    run()
