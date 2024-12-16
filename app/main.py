import os
import sys

from app.processors import builtin_processor_mapper, ExternalCommandProcessor, is_external_command


def main():
    # Wait for user input
    while True:
        sys.stdout.write("$ ")
        command = input()

        parts = command.split(" ")
        cmd = parts[0]

        if cmd in builtin_processor_mapper:
            processor = builtin_processor_mapper[cmd]
            processor.process(command)
        elif is_external_command(cmd):
            processor = ExternalCommandProcessor()
            processor.process(command)
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
