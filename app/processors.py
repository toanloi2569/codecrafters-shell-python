import sys
import abc


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
        param = command[5:]
        if param in shell_builtins:
            print(f"{param} is a shell builtin")
        else:
            print(f"{param}: not found")

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
