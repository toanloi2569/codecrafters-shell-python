import os
import sys

from app.processors import split_text, process_command, find_redirect_idx, write_file


def main():
    # Wait for user input
    while True:
        # sys.stdout.write("$ ")
        # command = input()
        command = input("$ ")

        parts = split_text(command)
        redirect_idx, opr = find_redirect_idx(parts)
        if redirect_idx != -1:
            command = ''.join(parts[:redirect_idx])
            file_name = ''.join(parts[redirect_idx+1:])
            file_name = file_name.strip()

            result, err = process_command(command)
            if opr == '>' or opr == '1>':
                if err:
                    sys.stderr.write(err + '\n')
                write_file(result, file_name)
            elif opr == '2>':
                if result:
                    sys.stdout.write(result + '\n')
                write_file(err, file_name)
        else:
            result, err = process_command(command)
            if err:
                err = err.strip()
                sys.stderr.write(err + '\n')
            elif result:
                result = result.strip()
                sys.stdout.write(result + '\n')


if __name__ == "__main__":
    main()
