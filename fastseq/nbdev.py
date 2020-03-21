import json
import sys
import re
from os import path

header_comment = "# %%\n"
split_re = "(#.*%%)"


def nb2py(notebook):
    result = []
    cells = notebook["cells"]

    for cell in cells:
        cell_type = cell["cell_type"]

        if cell_type == "markdown":
            result.append("%s'''\n%s\n'''" % (header_comment, "".join(cell["source"])))

        if cell_type == "code":
            result.append("%s%s" % (header_comment, "".join(cell["source"])))

    return "\n\n".join(result)


def py2nb(py_str):
    # remove leading header comment
    if py_str.startswith(header_comment):
        py_str = py_str[len(header_comment) :]

    cells = []
    chunks = re.split(split_re, py_str)

    for chunk in chunks:
        cell_type = "code"
        if (
            chunk.startswith("'''")
            or chunk.startswith("#markdown")
            or chunk.startswith("# markdown")
        ):
            chunk = chunk.strip("'\n")
            cell_type = "markdown"

        cell = {
            "cell_type": cell_type,
            "metadata": {},
            "source": chunk.splitlines(True),
        }

        if cell_type == "code":
            cell.update({"outputs": [], "execution_count": None})

        cells.append(cell)

    notebook = {
        "cells": cells,
        "metadata": {
            "anaconda-cloud": {},
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.7",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 1,
    }

    return notebook


def convert(in_file: str = None, out_file=None):
    if out_file is None and in_file[-3:] == ".py":
        out_file = in_file.replace(".py", ".ipynb")
    _, in_ext = path.splitext(in_file)
    _, out_ext = path.splitext(out_file)

    if in_ext == ".ipynb" and out_ext == ".py":
        with open(in_file, "r") as f:
            notebook = json.load(f)
        py_str = nb2py(notebook)
        with open(out_file, "w") as f:
            f.write(py_str)

    elif in_ext == ".py" and out_ext == ".ipynb":
        with open(in_file, "r") as f:
            py_str = f.read()
        notebook = py2nb(py_str)
        with open(out_file, "w") as f:
            json.dump(notebook, f, indent=2)
    else:
        raise (Exception("Extensions must be .ipynb and .py or vice versa"))
