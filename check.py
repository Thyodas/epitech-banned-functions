#!/usr/bin/env python3
import os
import sys
import errno

def execute_gdb(binary_name):
    os.system(f"gdb '{binary_name}' -ex 'source gdb_script.py' -ex \
'quit' > /dev/null")

def get_function_list() -> list[str]:
    try:
        f = open("function_list.result", "r")
    except OSError as e:
        print(f"Check.py: could not read function_list.result: {e.errno}")
        sys.exit(os.EX_OSFILE)
    with f:
        return(f.readlines())

if __name__ == '__main__':
    args = sys.argv[1:]
    if (len(args) != 1):
        print(f'Error: wrong number of arguments, found {len(args)} but \
expected 1.\nTry again with -h for help.')
        sys.exit(1)
    if args[0] == '-h' or args[0] == '--help':
        print("Usage: check.py {options | binary_name}\n\
Options:\n\
\t-h, --help Show this message")
        sys.exit(0)

    execute_gdb(args[0])
    func_list = get_function_list()
    for func in func_list:
        print(func[:-1])

