import os
import sys

from app.processors import split_text, process_command, RedirectionStdOutProcessor


def main():
    # Wait for user input
    while True:
        # sys.stdout.write("$ ")
        # command = input()
        command = input("$ ")

        parts = split_text(command)
        if '>' in parts:
            idx = parts.index('>')
            parts[idx] = '1>'

        if '1>' in parts:
            idx = parts.index('1>')

            command = ''.join(parts[:idx])
            file_name = ''.join(parts[idx+1:])
            file_name = file_name.strip()

            redirect_std_out = RedirectionStdOutProcessor()
            result, err = redirect_std_out.process(command)
            if err:
                sys.stderr.write(err + '\n')
            redirect_std_out.write(result, file_name)
        else:
            result, err = process_command(command)
            if err:
                sys.stderr.write(err + '\n')
            else:
                sys.stdout.write(result + '\n')


if __name__ == "__main__":
    main()
