from pyswip_notebook import IsolatedProlog
from pyswip import Functor
from pyswip.prolog import PrologError

DEFAULT_LIMIT = 10

rules = set()
prolog = IsolatedProlog()

def format_value(value):
    output = ""
    if isinstance(value, list):
        output = "[ " + ", ".join([format_value(val) for val in value]) + " ]"
    elif isinstance(value, Functor) and value.arity == 2:
        output = "{0}{1}{2}".format(value.args[0], value.name, value.args[1])
    else:
        output = "{}".format(value)

    return output

def format_result(result):
    result = list(result)

    if len(result) == 0:
        return "false."

    if len(result) == 1 and len(result[0]) == 0:
        return "true."

    output = ""
    for res in result:
        tmpOutput = []
        for var in res:
            tmpOutput.append(var + " = " + format_value(res[var]))
        output += ", ".join(tmpOutput) + " ;\n"
    output = output[:-3] + " ."

    return output

def run(code):
    global rules
    global prolog
    output = []
    ok = True
    numRules = 0

    tmp = ""
    isQuery = False
    for line in code.split("\n"):
        line = line.strip()
        if line == "" or line[0] == "%":
            continue
        line = line.split("%")[0].strip()
        if line == "!reset":
            output = []
            ok = True
            numRules = 0
            tmp = ""
            isQuery = False
            rules = set()
            prolog = IsolatedProlog()
            continue
        
        if line[:2] == "?-":
            isQuery = True
            line = line[2:]

        tmp += " " + line

        if tmp[-1] == ".":
            # End of statement
            tmp = tmp[:-1] # Removes "."
            maxresults = DEFAULT_LIMIT
            # Checks for maxresults
            if tmp[-1] == "}":
                tmp = tmp[:-1] # Removes "."
                limitStart = tmp.rfind('{')
                if limitStart == -1:
                    ok = False
                    output.append("ERROR: Found '}' before '.' but opening '{' is missing!")
                else:
                    limit = tmp[limitStart+1:]
                    try:
                        maxresults = int(limit)
                    except:
                        ok = False
                        output.append("ERROR: Invalid limit {" + limit + "}!")
                    tmp = tmp[:limitStart]

            try:
                if isQuery:
                    result = prolog.query(f"({tmp})", maxresult=maxresults)
                    output.append(format_result(result))
                    result.close()
                elif (tmp not in rules):
                    numRules += 1
                    rules.add(tmp)
                    prolog.assertz('(' + tmp + ')')
            except PrologError as error:
                ok = False
                output.append("ERROR: {}".format(error))

            tmp = ""
            isQuery = False

    if numRules > 0:
        output.append("Added " + str(numRules) + " clauses(s).")
        numRules = 0

    return output, ok
