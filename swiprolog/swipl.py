import os
import os.path as op
import tempfile
from pyswip import Prolog
from pyswip.prolog import PrologError

def format_result(result):
    result = list(result)

    if len(result) == 0:
        return "false."

    if len(result) == 1 and len(result[0]) == 0:
        return "true."

    output = ""
    for res in result:
        for var in res:
            output += var + " = " + res[var] + ", "
        output = output[:-2] + " ;\n"
    output = output[:-3] + " ."

    return output

def run(code):
    prolog = Prolog()

    output = []
    ok = True

    tmp = ""
    isQuery = False
    for line in code.split("\n"):
        line = line.strip()
        if line == "":
            continue

        if line[:2] == "?-":
            isQuery = True
            line = line[2:]

        tmp += " " + line

        if tmp[-1] == ".":
            tmp = tmp[:-1]
            # End of statement
            try:
                if isQuery:
                    output.append(format_result(prolog.query(tmp)))
                else:
                    prolog.assertz(tmp)
            except PrologError as error:
                ok = False
                output.append("ERROR: {}".format(error))

            tmp = ""
            isQuery = False

    return output, ok
