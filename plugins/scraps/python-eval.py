

#   Gimp-Python - allows the writing of Gimp plugins in Python.
#   Copyright (C) 2006  Manish Singh <yosh@gimp.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

from gimpfu import *

print("after import")   # lkk v3

def code_eval(code):
    if code == '-':
        import sys
        code = sys.stdin

    # lkk v2.  Python 2 syntax
    # exec code in globals()
    # lkk v3
    exec(code, globals())

print("calling register")   # lkk v3
register(
        "python-fu-eval",
        "Evaluate Python code",
        "Evaluate python code under the python interpreter (primarily for batch mode)",
        "Manish Singh",
        "Manish Singh",
        "2006",
        None,
        None,
        [
            (PF_STRING, "code", "The code to evaluate", "")
        ],
        [],
        code_eval)

print("calling main")   # lkk v3
main()
