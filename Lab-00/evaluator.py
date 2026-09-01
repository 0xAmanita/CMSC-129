from line_parser import classify_token


# operand token -> int or float
def _to_number(token):
    return float(token) if "." in token else int(token)


# int-looking floats print without the trailing .0
def format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# evaluates a postfix token list against the symbol table (`variables`).
# Assignments overwrite `variables` in place, so a lookup here always sees
# each variable's most recently assigned value.
#
# Returns (result, error, used_vars): `used_vars` lists every variable
# successfully read from the symbol table while evaluating, in first-seen
# order, so the caller can fold it into the "variables used" output list.
def evaluate_postfix(tokens, variables):
    stack = []
    used_vars = []
    for token in tokens:
        kind = classify_token(token)

        if kind == "operand":
            stack.append(_to_number(token))
        elif kind == "identifier":
            if token not in variables:
                return None, f"Undefined variable {token}", used_vars
            if token not in used_vars:
                used_vars.append(token)
            stack.append(variables[token])
        else:
            if len(stack) < 2:
                return None, "Malformed expression", used_vars
            b = stack.pop()
            a = stack.pop()
            try:
                if token == "+":
                    stack.append(a + b)
                elif token == "-":
                    stack.append(a - b)
                elif token == "*":
                    stack.append(a * b)
                elif token == "/":
                    stack.append(a / b)
                elif token == "%":
                    stack.append(a % b)
            except ZeroDivisionError:
                return None, "Division by zero", used_vars

    if len(stack) != 1:
        return None, "Malformed expression", used_vars
    return stack[0], None, used_vars
