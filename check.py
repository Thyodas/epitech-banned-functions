#!/usr/bin/env python3
import os
import sys
import errno
import json

from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich.align import Align
from rich.tree import Tree
from rich import box

import re

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
        return(list(map(lambda x: x[:-1], f.readlines())))

def get_database() -> dict:
    try:
        f = open("allowed_functions.json")
        result = json.load(f)
        f.close()
    except Exception as e:
        print(f"Check.py: could not read allowed_functions.json: {e}")
        sys.exit(84)
    return result

def manage_args(args):
    if (len(args) < 1):
        print(f'Error: wrong number of arguments, found {len(args)} but \
expected 1.\nTry again with -h for help.')
        sys.exit(1)

    if args[0] == '-h' or args[0] == '--help':
        print("Usage: check.py {options | binary_name}\n\
Options:\n\
\t-h, --help Show this message")
        sys.exit(0)

def match_database(function, allowed_functions):
    for regex in allowed_functions:
        if regex[-1] != "*":
            regex = regex + "$"
        if re.match(regex, function):
            return True
    return False

def show_result_with_data(func_list, allowed_list):
    allowed_nb = 0
    warning_nb = 0
    banned_nb = 0
    result_table = Table(title="", show_lines=False, expand="True", box=box.ROUNDED)
    result_table.add_column(Text("Function", style="bold"))
    result_table.add_column(Text("Result", style="bold"))
    for func in func_list:
        if match_database(func, allowed_list):
            result_table.add_row(func, "[bold green]:heavy_check_mark:")
            allowed_nb += 1
        elif func[0] == '_':
            result_table.add_row(f"[bold yellow]{func}", "[yellow][reverse] WARNING [/reverse] Unknown function")
            warning_nb += 1
        else:
            result_table.add_row(f"[bold red]{func}", "[red][reverse] ALERT [/reverse] Banned function")
            banned_nb += 1
    print(result_table)
    return banned_nb, warning_nb, allowed_nb

def show_result_without_data(func_list):
    result_table = Table(title="", show_lines=False, expand="True", box=box.ROUNDED)
    result_table.add_column(Text("Function", style="bold"))
    for func in func_list:
        result_table.add_row(func)
    print(result_table)

def show_recap(banned_nb, warning_nb, allowed_nb):
    recap_table = Table(title_style="bold not italic", expand=True, box=None)
    recap_table.add_column(Text("Banned"), justify="center", style="red bold")
    recap_table.add_column(Text("Warning"), justify="center", style="bold yellow")
    recap_table.add_column(Text("Allowed"), justify="center", style="bold green")
    recap_table.add_row(str(banned_nb), str(warning_nb), str(allowed_nb))
    print(Panel(recap_table))

def show_manually_added(list):
    if list is None or len(list) == 0:
        return
    result_str = ""
    for el in list[:-1]:
        result_str += f"[green bold]{el}[not bold white], "
    result_str += f"[green bold]{list[-1]}"
    print(Panel(f"Manually added allowed functions: {result_str}"))

def show_title(binary_name, database):
    if binary_name in database["projects"].keys():
        module = database["projects"][binary_name]["module"]
        name = database["projects"][binary_name]["projectName"]
        print(Panel(Align(f"[bold]Detected [green]{module} {name}[/green]", align="center")))
    else:
        print(Panel(Align(f"[bold]Unknown project [green]{binary_name}[/green]", align="center")))

if __name__ == '__main__':
    args = sys.argv[1:]
    manage_args(args)
    execute_gdb(args[0])

    banned_nb, warning_nb, allowed_nb = 0, 0, 0
    binary_name = args[0].split('/')[-1]
    database = get_database()
    func_list = get_function_list()
    allowed_list = args[1:]
    func_list.append("test")
    if binary_name in database["projects"].keys():
        allowed_list.extend(database["projects"][binary_name]["allowedFunctions"])

    if len(allowed_list) == 0:
        print(Panel(Align(f"[bold]Unknown project [green]{binary_name}[/green]", align="center")))
        show_result_without_data(func_list)
        print(Panel("[blue][reverse] INFO [/reverse] This is just the list of all functions found in the binary. \
Allowed functions are detected via the binary name. You can manually add allowed functions via arguments."))
    else:
        show_title(binary_name, database)
        show_manually_added(args[1:])
        banned_nb, warning_nb, allowed_nb = show_result_with_data(func_list, allowed_list)
        show_recap(banned_nb, warning_nb, allowed_nb)
        if warning_nb > 0:
            print(Panel("[yellow][reverse] WARNING [/reverse] Some warnings require your attention."))
        if banned_nb > 0:
            print(Panel("[red][reverse] ALERT [/reverse] Banned functions were detected!"))
            exit(1)
        if banned_nb == 0 and warning_nb == 0:
            print(Panel("[green][reverse] OK [/reverse] All good, no problem found!"))
