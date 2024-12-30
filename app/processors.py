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

    for c in text:
        if c == ' ' and not doing:
            continue
        if c == ' ' and doing and not quote:
            done.append(doing)
            doing = ''
            continue
        if c == ' ' and doing and quote:
            doing += ' '
            continue

        if c == '\'' and quote == '\'':
            doing += '\''
            quote = ''
            done.append(doing)
            doing = ''
            continue
        if c == '\'' and quote == '\"':
            doing += '\''
            continue
        if c == '\'' and not quote and not doing:
            doing += '\''
            quote = '\''
            continue

        if c == '\"' and quote == '\"' and not backslash:
            doing += '\"'
            quote = ''
            done.append(doing)
            doing = ''
            continue
        if c == '\"' and quote == '\"' and backslash:
            doing += '\"'
            continue
        if c == '\"' and not quote and not doing:
            doing += '\"'
            quote = '\"'
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
        text = [p[1:-1] if p.startswith('\'') or p.startswith('\"') else p for p in text ]
        text = ' '.join(text)
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

        out = ''
        for file_name in files:
            if file_name.startswith('\"'):
                file_name = file_name[1:-1]
            if file_name.startswith('\''):
                file_name = file_name[1:-1]

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
