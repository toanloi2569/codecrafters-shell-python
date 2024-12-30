import os
import sys

from app.processors import builtin_processor_mapper, ExternalCommandProcessor, is_external_command, split_quoting, CustomCatProcessor


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
            parts = split_quoting(command)
            if len(parts) == 1:
                print(f"{command}: command not found")
                continue
            else:
                CustomCatProcessor().process(command)


if __name__ == "__main__":
    main()
