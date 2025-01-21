import re
import subprocess
import sys
import abc
import os
import typing
from abc import abstractmethod
from typing import Text, List

paths = os.environ.get("PATH").split(":")
home = os.environ.get("HOME")


def split_text(text: str):
    def handle_backslash(c: str, quote: str):
        # Return character after backslash
        if quote == '\"' and c in ['\\', '\"', '$']:
            return c
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
    def process(self, command) -> typing.Tuple[Text, Text]:
        pass

    @abc.abstractmethod
    def builtin_command(self):
        pass

class EchoProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "echo"

    def process(self, command):
        content = command[5:]
        text = split_text(content)
        text = ''.join(text)
        return text, ''


class TypeProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "type"

    def process(self, command):
        content = command[5:]

        if content in shell_builtins:
            return command[5:] + " is a shell builtin", ''

        if is_external_command(content):
            return f"{content} is {get_path_external_command(content)}", ''

        return f"{content}: not found", ''

class PwdProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "pwd"

    def process(self, command):
        return os.getcwd(), ''

class CdProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "cd"

    def process(self, command):
        if command[3:] == "~":
            os.chdir(home)
            return '', ''
        elif os.path.isdir(command[3:]):
            os.chdir(command[3:])
            return '', ''
        else:
            return f"cd: {command[3:]}: No such file or directory", ''

class CatProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "cat"

    def process(self, command):
        content = command[4:]

        files = split_text(content)
        files = [file for file in files if file != ' ']

        out, err = '', ''
        for file_name in files:
            if not os.path.isfile(file_name):
                err += f"cat: {file_name}: No such file or directory"
            else:
                with open(file_name, 'r') as f:
                    out += f.read()

        return out.strip(), err.strip()

class ExitProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "exit"

    def process(self, command):
        sys.exit(0)


class CustomCatProcessor(BuiltinProcessor):
    def builtin_command(self):
        return "cat"

    def process(self, command):
        parts = split_text(command)
        files = split_text(parts[1:])
        files = [file for file in files if file != ' ']

        out, err = '', ''
        for file_name in files:
            if not os.path.isfile(file_name):
                err += f"cat: {file_name}: No such file or directory"
            with open(file_name, 'r') as f:
                out += f.read()

        return out.strip(), err.strip()


def is_external_command(command):
    return command if command in external_commands else None

def get_path_external_command(command):
    for path in paths:
        if os.path.isfile(f"{path}/{command}"):
            return f"{path}/{command}"
    return None

class ExternalCommandProcessor(Processor):
    def process(self, command):
        result = subprocess.run(command, capture_output=True, shell=True)
        if result.stderr:
            return '', result.stderr.decode()
        return result.stdout.decode(), ''


def find_redirect_idx(parts):
    if '>' in parts:
        return parts.index('>'), '>'
    if '1>' in parts:
        return parts.index('1>'), '1>'
    if '2>' in parts:
        return parts.index('2>'), '2>'
    if '>>' in parts:
        return parts.index('>>'), '>>'
    if '1>>' in parts:
        return parts.index('1>>'), '1>>'
    if '2>>' in parts:
        return parts.index('2>>'), '2>>'
    return -1, None

def write_file(content, file_path, mode='w'):
    if os.path.isfile(file_path):
        with open(file_path, mode) as f:
            f.write(content)
    else:
        with open(file_path, 'x') as f:
            f.write(content.strip())


def process_command(command):
    parts = split_text(command)
    cmd = parts[0]
    if cmd in builtin_processor_mapper:
        processor = builtin_processor_mapper[cmd]
        result, err = processor.process(command)
        return result, err
    elif is_external_command(cmd):
        processor = ExternalCommandProcessor()
        result, err = processor.process(command)
        return result, err
    else:
        parts = split_text(command)
        if len(parts) == 1:
            return '', f"{command}: command not found"
        else:
            processor = CustomCatProcessor()
            result, err = processor.process(command)
            return result, err


shell_builtins = ["echo", "type", "exit", "pwd", "cd"]
builtin_processor_mapper = {
    "echo": EchoProcessor(),
    "type": TypeProcessor(),
    "exit": ExitProcessor(),
    "pwd": PwdProcessor(),
    "cd": CdProcessor(),
    "cat": CatProcessor(),
}
external_commands = [
    f for path in paths if os.path.isdir(path)
    for f in os.listdir(path) if os.path.isfile(f"{path}/{f}")
]
