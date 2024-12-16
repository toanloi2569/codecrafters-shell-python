import sys
import abc
import os

paths = os.environ.get("PATH").split(":")

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
        print(command[5:])

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


shell_builtins = ["echo", "type", "exit"]
builtin_processor_mapper = {
    "echo": EchoProcessor(),
    "type": TypeProcessor(),
    "exit": ExitProcessor()
}
