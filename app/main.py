import os
import sys

from app.processors import builtin_processor_mapper, ExternalCommandProcessor, is_external_command, split_text, \
    CustomCatProcessor, process_command, RedirectionStdOutProcessor


def main():
    # Wait for user input
    while True:
        sys.stdout.write("$ ")
        command = input()

        parts = split_text(command)
        print(parts)
        if len(parts) > 3 and parts[-3] in ['>', '1>']:
            command = ''.join(parts[:-3])
            file = parts[-1]
            redirect_std_out = RedirectionStdOutProcessor()
            result = redirect_std_out.process(command)
            print(result)
            redirect_std_out.write(result, file)
        else:
            print(process_command(command))


if __name__ == "__main__":
    main()
