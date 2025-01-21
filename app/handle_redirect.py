import os
import sys


def write_file(content, file_path, mode='w'):
    if os.path.isfile(file_path):
        with open(file_path, mode) as f:
            f.write(content)
    else:
        with open(file_path, 'x') as f:
            f.write(content.strip())


def find_redirect_idx(parts):
    """
    Tìm vị trí và loại redirect trong lệnh.
    Trả về: (vị trí_redirect, loại_redirect)
    """
    redirect_operators = ['>', '1>', '2>', '>>', '1>>', '2>>']
    for idx, part in enumerate(parts):
        if part in redirect_operators:
            return idx, part
    return -1, None


def handle_redirect(file_name, opr, result, err):
    redirect_handlers = {
        '>': lambda: write_file(result, file_name),
        '1>': lambda: write_file(result, file_name),
        '2>': lambda: write_file(err, file_name),
        '>>': lambda: write_file('\n' + result, file_name, mode='a'),
        '1>>': lambda: write_file('\n' + result, file_name, mode='a'),
        '2>>': lambda: write_file('\n' + err, file_name, mode='a')
    }

    redirect_handlers[opr]()
