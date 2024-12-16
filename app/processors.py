import sys
import abc
import os


class Processor(abc.ABC):
    @abc.abstractmethod
    def process(self, command):
        pass

    @abc.abstractmethod
    def builtin_command(self):
        pass

class EchoProcessor(Processor):
    def builtin_command(self):
        return "echo"

    def process(self, command):
        print(command[5:])

class TypeProcessor(Processor):
    def builtin_command(self):
        return "type"

    def process(self, command):
        path_list = os.environ.get("PATH")
        paths = path_list.split(":")


        if command[5:] in shell_builtins:
            print(command[5:] + " is a shell builtin")
            return

        for path in paths:
            if os.path.isfile(path + "/" + command[5:]):
                print(command[5:] + " is " + path + "/" + command[5:])
                return

        print(f"{command[5:]}: not found")

class ExitProcessor(Processor):
    def builtin_command(self):
        return "exit"

    def process(self, command):
        sys.exit(0)


shell_builtins = ["echo", "type", "exit"]
processor_mapper = {
    "echo": EchoProcessor(),
    "type": TypeProcessor(),
    "exit": ExitProcessor()
}
