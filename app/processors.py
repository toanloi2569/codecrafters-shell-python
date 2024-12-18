import re
import sys
import abc
import os
import typing
from typing import Text, List

paths = os.environ.get("PATH").split(":")
home = os.environ.get("HOME")

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
        if '\'' in content:
            print(content[1:-1])
        else:
            print(re.sub(r'\s+', ' ', content))

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

        files = []
        
        parts = re.split(r' \'|\' ', content)
        for part in parts:
            if part.startswith('\'')  and part.endswith('\''):
                # part = part.replace(' ', '\\ ')
                files.append(part[1:-1])
            elif part.startswith('\'') and not part.endswith('\''):
                # part = part.replace(' ', '\\ ')
                # files.append(f'{part}\'')
                files.append(part[1:])
            elif part.endswith('\'') and not part.startswith('\''):
                # part = part.replace(' ', '\\ ')
                # files.append(f'\'{part}')
                files.append(part[:-1])
            else:
                p_ = part.split(' ')
                p_ = [_.strip() for _ in p_ if len(_.strip()) > 0 ]
                files.extend(p_)

        out = ''
        for file_name in files:
            with open(file_name, 'r') as f:
                out += f.read()
                # print(out)
        
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
