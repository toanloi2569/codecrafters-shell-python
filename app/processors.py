import re
import sys
import abc
import os
import typing
from typing import Text, List

paths = os.environ.get("PATH").split(":")
home = os.environ.get("HOME")


def split_quoting(text: str):
    def handle_backslash(c: str, quote: str):
        # Return character after backslash
        if quote == '\"' and c in ['\\', '\"', '$']:
            return c
        # if quote == '\'' and c == '\\':
        #     return c
        if not quote:
            return c
        return '\\' + c

    def handle_quote(c: str, quote: str, doing: str):
        # Return quote, doing, is_closing
        if quote == c:  # Closing quote
            return '', doing, True
        elif not quote:  # Opening quote
            return c, doing, False
        else:  # Inside a different quote
            return quote, doing + c, False

    def handle_space(doing: str, quote: str, done: list):
        # Return doing, done
        if quote:
            return doing + ' ', done
        if doing:
            done.append(doing)
            done.append(' ')
            return '', done

        done.append(' ')
        return '', done

    def finalize_token(doing: str, quote: str):
        if quote:
            raise ValueError("Unclosed quote")
        return doing


    done: list = []             # Completed text list
    doing: str = ''             # Processing string
    quote: str = ''             # Quote is being processed
    backslash: bool = False    # Backslash is being processed

    for i, c in enumerate(text):
        if backslash:
            doing += handle_backslash(c, quote)
            backslash = False
            continue

        if c == '\\':
            backslash = True
            continue

        if c in ['\'', '\"']:
            quote, doing, is_closing = handle_quote(c, quote, doing)
            if is_closing:
                done.append(doing)
                doing = ''
            continue

        if c == ' ':
            doing, done = handle_space(doing, quote, done)
            continue

        doing += c

    if doing:
        done.append(finalize_token(doing, quote))

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

class CustomCatProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "cat"

    def process(self, command):
        parts = split_quoting(command)
        files = split_quoting(parts[1:])
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
