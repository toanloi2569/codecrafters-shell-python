import sys

from app.processors import processor_mapper


def main():
    # Wait for user input
    while True:
        sys.stdout.write("$ ")
        command = input()

        parts = command.split(" ")
        builtin_command = parts[0]

        if builtin_command in processor_mapper:
            processor = processor_mapper[builtin_command]
            processor.process(command)
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
