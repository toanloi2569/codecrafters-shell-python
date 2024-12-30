import os
import sys

from app.processors import split_text, process_command, find_redirect_idx, write_file


def main():
    # Wait for user input
    while True:
        command = input("$ ")
        parts = split_text(command)

        # Xử lý trường hợp có redirect output
        # Gồm các trường hợp: >, 1>, 2>, >>, 1>>, 2>>
        redirect_idx, opr = find_redirect_idx(parts)
        if redirect_idx != -1:
            command = ''.join(parts[:redirect_idx])
            file_name = ''.join(parts[redirect_idx+1:])
            file_name = file_name.strip()

            result, err = process_command(command)
            result = result.strip()
            err = err.strip()
            if opr == '>' or opr == '1>':
                if err:
                    sys.stderr.write(err + '\n')
                write_file(result, file_name)
            elif opr == '2>':
                if result:
                    sys.stdout.write(result + '\n')
                write_file(err, file_name)
            elif opr == '>>' or opr == '1>>':
                if err:
                    sys.stderr.write(err + '\n')
                write_file('\n' + result, file_name, mode='a')
            elif opr == '2>>':
                if result:
                    sys.stdout.write(result + '\n')
                write_file('\n' + err, file_name, mode='a')
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
