import readline
import sys

from app.processors import split_text, process_command, builtin_processor_mapper, external_commands
from app.handle_redirect import write_file, find_redirect_idx, handle_redirect


def auto_complete(text, state):
    options = [i + ' ' for i in builtin_processor_mapper.keys() if i.startswith(text)]
    options += [i + ' ' for i in external_commands if i.startswith(text)]

    try:
        return options[state]
    except IndexError:
        return None

def display_matches(substitution, matches, longest_match_length):
    if len(matches) > 1:
        sys.stdout.write('\n')
        sys.stdout.write(' '.join(matches).strip() + '\n')
        sys.stdout.write('$ ' + substitution)
    elif len(matches) == 1:
        readline.insert_text(matches[0])
        readline.redisplay()

readline.parse_and_bind("tab: complete")
readline.set_completer(auto_complete)
readline.set_completion_display_matches_hook(display_matches)


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

            result, err = process_command(command)
            file_name, result, err = file_name.strip(), result.strip(), err.strip()
            handle_redirect(file_name, opr, result, err)
        else:
            result, err = process_command(command)
            result, err = result.strip(), err.strip()
            if err:
                sys.stderr.write(err + '\n')
            elif result:
                sys.stdout.write(result + '\n')


if __name__ == "__main__":
    main()
