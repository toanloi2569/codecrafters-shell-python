import re
import sys
import abc
import os
import typing
from typing import Text, List

paths = os.environ.get("PATH").split(":")
home = os.environ.get("HOME")


def split_quoting(text: str):
    # Completed text list
    done: list = []

    # Processing str
    doing: str = ''

    # Quote is being processed
    quote: str = ''

    # Is backslash being used?
    backslash: bool = False

    for i, c in enumerate(text):
        if c == ' ' and backslash:
            doing += ' '
            backslash = False
            continue
        if c == ' ' and not doing:
            done.append(' ')
            continue
        if c == ' ' and doing and not quote:
            done.append(doing)
            done.append(' ')
            doing = ''
            continue
        if c == ' ' and doing and quote:
            doing += ' '
            continue

        if c == '\'' and backslash:
            doing += '\''
            backslash = False
            continue
        if c == '\'' and quote == '\'':
            quote = ''
            done.append(doing)
            doing = ''
            continue
        if c == '\'' and quote == '\"':
            doing += '\''
            continue
        if c == '\'' and not quote and not doing:
            quote = '\''
            continue

        if c == '\"' and backslash:
            doing += '\"'
            backslash = False
            continue
        if c == '\"' and quote == '\"' and not backslash:
            quote = ''
            done.append(doing)
            doing = ''
            continue
        if c == '\"' and quote == '\"' and backslash:
            doing += '\"'
            continue
        if c == '\"' and quote == '\'':
            doing += '\"'
            continue
        if c == '\"' and not quote and not doing:
            quote = '\"'
            continue

        # Tương tác giữa dấu nháy kép (") và dấu backslash (\)
        #       Dấu nháy kép bảo toàn hầu hết các ký tự bên trong nó, ngoại trừ:
        #           Ký tự " (phải đóng dấu trích dẫn).
        #           Ký tự $ (biến thay thế).
        #           Ký tự \ (có ngữ cảnh đặc biệt).
        #       Khi dấu \ được sử dụng trong dấu ", nó sẽ kiểm tra xem ký tự tiếp theo có phải 1 trong 3 ký tự sau không: \, ", $
        #       Nếu có, ký tự \ sẽ được hiểu là ký tự escape và sẽ in ra ký tự tiếp theo
        #       Nếu không, ký tự \ sẽ được hiểu là ký tự bình thường và sẽ in ra ký tự \ đó
        # Tương tác giữa dấu nháy đơn (') và dấu backslash (\)
        #       Dấu nháy đơn bảo toàn tất cả các ký tự bên trong nó, ngoại trừ ký tự ' (phải đóng dấu trích dẫn).
        #       Khi dấu \ được sử dụng trong dấu ', nó sẽ được in ra như là ký tự bình thường
        if c == '\\' and quote == '\"' and  i+1 < len(text) and text[i+1] in ['\\', '\"', '$'] and not backslash:
            backslash = True
            continue
        if c == '\\' and backslash:
            doing += '\\'
            backslash = False
            continue
        if c == '\\' and not quote:
            backslash = True
            continue
        if c == '\\' and quote:
            doing += '\\'
            continue

        if c != ' ' and c != '\'' and c != '\"':
            doing += c
            continue

        raise ValueError

    if doing:
        if ((doing.startswith('\'') and not doing.endswith('\''))
                or (doing.startswith('\"') and not doing.endswith('\"'))):
            raise ValueError
        done.append(doing)

    excess_space_idx = []
    for i, s in enumerate(done):
        if s == ' ' and i + 1 < len(done) and done[i+1] == ' ':
            excess_space_idx.append(i)
    done = [ s for i, s in enumerate(done) if i not in excess_space_idx ]

    return done

class Processor(abc.ABC):
    @abc.abstractmethod
    def process(self, command):
        pass

class BuiltinProcessor(Processor):
    @abc.abstractmethod
    def process(self, command):
        pass

    @abc.abstractmethod
    def builtin_command(self):
        pass

class EchoProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "echo"

    def process(self, command):
        content = command[5:]
        text = split_quoting(content)
        # text = [p[1:-1] if p.startswith('\'') or p.startswith('\"') else p for p in text ]
        text = ''.join(text)
        print(text)


class TypeProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "type"

    def process(self, command):
        content = command[5:]

        if content in shell_builtins:
            print(command[5:] + " is a shell builtin")
            return

        if is_external_command(content):
            print(f"{content} is {is_external_command(content)}")
            return

        print(f"{content}: not found")

class PwdProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "pwd"

    def process(self, command):
        print(os.getcwd())

class CdProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "cd"

    def process(self, command):
        if command[3:] == "~":
            os.chdir(home)
        elif os.path.isdir(command[3:]):
            os.chdir(command[3:])
        else:
            print(f"cd: {command[3:]}: No such file or directory")

class CatProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "cat"

    def process(self, command):
        content = command[4:]

        files = split_quoting(content)
        files = [file for file in files if os.path.isfile(file)]
        out = ''
        for file_name in files:
            with open(file_name, 'r') as f:
                out += f.read()

        print(out.strip())

class ExitProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "exit"

    def process(self, command):
        sys.exit(0)


def is_external_command(command):
    for path in paths:
        if os.path.isfile(f"{path}/{command}"):
            return f"{path}/{command}"

class ExternalCommandProcessor(Processor):
    def process(self, command):
        os.system(command)


shell_builtins = ["echo", "type", "exit", "pwd", "cd"]
builtin_processor_mapper = {
    "echo": EchoProcessor(),
    "type": TypeProcessor(),
    "exit": ExitProcessor(),
    "pwd": PwdProcessor(),
    "cd": CdProcessor(),
    "cat": CatProcessor()
}
