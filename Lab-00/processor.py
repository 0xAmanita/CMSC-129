from evaluator import evaluate_postfix, format_number
from line_parser import INVALID_MESSAGE, parse_line
from postfix_converter import infix_to_postfix


def evaluate_line(line, variables):
    """Parse, convert, and evaluate one line; updates variables in place."""
    parsed = parse_line(line)

    if parsed.kind == "invalid":
        return {
            "line": parsed.raw.strip(),
            "postfix": INVALID_MESSAGE,
            "result_line": INVALID_MESSAGE,
            "var_name": None,
            "used_vars": [],
            "error": parsed.error,
        }

    postfix = infix_to_postfix(parsed.expression)
    value, error, used_vars = evaluate_postfix(postfix, variables)

    if error:
        # Leave the symbol table untouched: a statement like `x = 1 / 0`
        # keeps x's previous value (or stays undefined if it never had one).
        return {
            "line": parsed.raw.strip(),
            "postfix": " ".join(postfix),
            "result_line": "error",
            "var_name": None,
            "used_vars": used_vars,
            "error": error,
        }

    if parsed.kind == "statement":
        variables[parsed.var_name] = value
        result_line = f"{parsed.var_name} = {format_number(value)}"
        var_name = parsed.var_name
    else:
        result_line = format_number(value)
        var_name = None

    return {
        "line": parsed.raw.strip(),
        "postfix": " ".join(postfix),
        "result_line": result_line,
        "var_name": var_name,
        "used_vars": used_vars,
        "error": None,
    }


def process_lines(lines):
    """Evaluate a sequence of raw input lines against a shared symbol table."""
    entries = []
    variables_used = []
    errors = []
    variables = {}

    for line in lines:
        entry = evaluate_line(line, variables)
        entries.append(entry)

        for used in entry.get("used_vars", []):
            if used not in variables_used:
                variables_used.append(used)
        if entry.get("var_name") and entry["var_name"] not in variables_used:
            variables_used.append(entry["var_name"])
        if entry.get("error"):
            errors.append(entry["error"])

    return entries, variables_used, errors, variables


def build_output_text(entries, variables_used, errors, variables):
    """Format the results the way the spec's mockup shows."""
    blocks = []
    for entry in entries:
        block = (
            f"Line: {entry['line']}\n"
            f"Postfix: {entry['postfix']}\n"
            f"Result: {entry['result_line']}"
        )
        blocks.append(block)

    output = "\n\n".join(blocks)

    separator = "-" * 43
    output += f"\n\n{separator}\n"
    output += "Variables used:\n"
    if variables_used:
        output += "\n".join(
            f"{name} = {format_number(variables[name])}" for name in variables_used
        ) + "\n"
    else:
        output += "(none)\n"

    output += f"{separator}\n"
    output += "Errors found:\n"
    if errors:
        output += "\n".join(errors) + "\n"
    else:
        output += "(none)\n"

    return output
