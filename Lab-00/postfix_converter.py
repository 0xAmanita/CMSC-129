from line_parser import classify_token, tokenize

_PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}


# grabs the single token or the whole (...) group starting at tokens[i]
def _consume_atom(tokens, i):
    if tokens[i] == "(":
        depth = 0
        j = i
        while j < len(tokens):
            if tokens[j] == "(":
                depth += 1
            elif tokens[j] == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        return tokens[i:j], j
    return [tokens[i]], i + 1


# rewrites unary +/- runs into "(0 - atom)" so the shunting-yard step
# only ever has to deal with binary + - * / %
def _desugar_unary(tokens):
    result = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        prev_kind = classify_token(result[-1]) if result else None
        at_sign_position = token in ("+", "-") and (not result or prev_kind in ("operator", "lparen"))

        if at_sign_position:
            negative = False
            while i < len(tokens) and tokens[i] in ("+", "-"):
                negative ^= tokens[i] == "-"
                i += 1
            if negative:
                atom, i = _consume_atom(tokens, i)
                result.extend(["(", "0", "-", *atom, ")"])
            continue

        result.append(token)
        i += 1

    return result


# shunting-yard: infix expression string -> list of postfix tokens
def infix_to_postfix(expression):
    tokens = _desugar_unary(tokenize(expression))
    output = []
    op_stack = []

    for token in tokens:
        kind = classify_token(token)

        if kind in ("operand", "identifier"):
            output.append(token)

        elif kind == "lparen":
            op_stack.append(token)

        elif kind == "rparen":
            while op_stack[-1] != "(":
                output.append(op_stack.pop())
            op_stack.pop()

        else:  # operator
            while (
                op_stack
                and op_stack[-1] != "("
                and _PRECEDENCE[op_stack[-1]] >= _PRECEDENCE[token]
            ):
                output.append(op_stack.pop())
            op_stack.append(token)

    while op_stack:
        output.append(op_stack.pop())

    return output
