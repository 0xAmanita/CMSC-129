import re
from dataclasses import dataclass
from typing import Optional

INVALID_MESSAGE = "Invalid input code."

_OPERATORS = set("+-*/%")

_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
_NUMBER_RE = re.compile(r"^\d+(\.\d+)?$")

# tokens an expression can be made of
_TOKEN_RE = re.compile(
    r"""
      \s+
    | \d+\.\d+
    | \d+
    | [A-Za-z][A-Za-z0-9_]*
    | [+\-*/%()]
    """,
    re.VERBOSE,
)


@dataclass
class ParsedLine:
    raw: str
    kind: str  # "statement" | "expression" | "invalid"
    var_name: Optional[str] = None
    expression: Optional[str] = None
    error: Optional[str] = None


# C rules, minus underscores; keywords are allowed as names here
def is_valid_variable_name(name):
    if not name:
        return False
    return bool(_IDENTIFIER_RE.match(name))


# splits expression into tokens: None means an illegal character was found
def tokenize(expression):
    tokens = []
    pos = 0
    for match in _TOKEN_RE.finditer(expression):
        if match.start() != pos:
            return None
        pos = match.end()
        text = match.group()
        if text.strip():
            tokens.append(text)
    if pos != len(expression):
        return None
    return tokens


# labels a token as operand, operator, paren, or identifier
def classify_token(token):
    if _NUMBER_RE.match(token):
        return "operand"
    if token in _OPERATORS:
        return "operator"
    if token == "(":
        return "lparen"
    if token == ")":
        return "rparen"
    return "identifier"


# checks token order/parens are valid; returns None if ok, else a reason
def _validate_expression(expression):
    if expression.strip() == "":
        return "empty expression"

    tokens = tokenize(expression)
    if not tokens:
        return "illegal character" if tokens is None else "empty expression"

    depth = 0
    expect = "operand"  # kind of token that may legally come next

    for i, token in enumerate(tokens):
        kind = classify_token(token)

        if kind == "identifier" and not is_valid_variable_name(token):
            return f"invalid variable name '{token}'"

        if kind == "lparen":
            if expect != "operand":
                return "unexpected '('"
            depth += 1

        elif kind == "rparen":
            if expect != "operator" or depth == 0:
                return "unexpected ')'"
            depth -= 1
            expect = "operator"

        elif kind in ("operand", "identifier"):
            if expect != "operand":
                return "operand in operator position"
            expect = "operator"

        elif kind == "operator":
            if expect == "operand":
                prev_kind = classify_token(tokens[i - 1]) if i > 0 else None
                if token in ("+", "-") and prev_kind in (None, "operator", "lparen"):
                    continue  # unary +/-, still expecting an operand
                return "operator in operand position"
            expect = "operand"

    if depth != 0:
        return "unbalanced parentheses"
    if expect != "operator":
        return "expression ends with an operator"

    return None


# classifies a line as a statement, an expression, or invalid
def parse_line(line):
    raw = line.rstrip("\n")
    stripped = raw.strip()

    if stripped == "":
        return ParsedLine(raw, "invalid", error=INVALID_MESSAGE)

    eq_count = stripped.count("=")
    if eq_count > 1:
        return ParsedLine(raw, "invalid", error=INVALID_MESSAGE)

    # statement: identifier = expression
    if eq_count == 1:
        lhs, rhs = stripped.split("=", 1)
        var_name = lhs.strip()
        expression = rhs.strip()

        if not is_valid_variable_name(var_name):
            return ParsedLine(raw, "invalid", error=INVALID_MESSAGE)
        if _validate_expression(expression) is not None:
            return ParsedLine(raw, "invalid", error=INVALID_MESSAGE)

        return ParsedLine(raw, "statement", var_name=var_name, expression=expression)

    # otherwise: plain expression, no assignment
    if _validate_expression(stripped) is not None:
        return ParsedLine(raw, "invalid", error=INVALID_MESSAGE)

    return ParsedLine(raw, "expression", expression=stripped)
    # basta oy!
