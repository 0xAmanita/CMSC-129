from line_parser import classify_token


# operand token -> int or float
def _to_number(token):
    return float(token) if "." in token else int(token)


# int-looking floats print without the trailing .0
def format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# evaluates a postfix token list against known variables
def evaluate_postfix(tokens, variables):
    stack = []
    for token in tokens:
        kind = classify_token(token)

        if kind == "operand":
            stack.append(_to_number(token))
        elif kind == "identifier":
            if token not in variables:
                return None, f"undefined variable '{token}'"
            stack.append(variables[token])
        else:
            if len(stack) < 2:
                return None, "malformed expression"
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
                elif token == "^":
                    stack.append(a ** b)
            except ZeroDivisionError:
                return None, "division by zero"

    if len(stack) != 1:
        return None, "malformed expression"
    return stack[0], None
