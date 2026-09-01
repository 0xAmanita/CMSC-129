import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from evaluator import evaluate_postfix, format_number
from line_parser import INVALID_MESSAGE, parse_line
from postfix_converter import infix_to_postfix


class ExpressionEvaluatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PE00 - Expression Evaluation")
        self.root.geometry("900x550")

        self._build_ui()

        # Input starts empty, so keep Process disabled until there is text.
        self.process_button.config(state=tk.DISABLED)

    def _build_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input side (left, editable)
        input_frame = tk.Frame(main_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(input_frame, text="Input lines:", anchor="w").pack(fill=tk.X)
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Toggle Process on/off as the input area changes.
        self.input_text.bind("<<Modified>>", self._on_input_modified)

        # Output side (right, read-only)
        output_frame = tk.Frame(main_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(output_frame, text="Output:", anchor="w").pack(fill=tk.X)
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.load_button = tk.Button(
            button_frame, text="Load File", command=self.load_file
        )
        self.load_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.process_button = tk.Button(
            button_frame, text="Process", command=self.process_input
        )
        self.process_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    def _on_input_modified(self, event):
        """Enable Process only when the input area has content."""
        content = self.input_text.get("1.0", tk.END)
        self.input_text.edit_modified(False)  # reset flag so event re-fires

        if content.strip() == "":
            self.process_button.config(state=tk.DISABLED)
        else:
            self.process_button.config(state=tk.NORMAL)

    def load_file(self):
        """Load a .in file into the input area, replacing current content."""
        file_path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Input files", "*.in"), ("All files", "*.*")],
        )
        if not file_path:
            return  # user cancelled

        try:
            with open(file_path, "r") as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")
            return

        self.input_text.delete("1.0", tk.END)  # overwrite current content
        self.input_text.insert("1.0", content)  # this re-enables Process

    def process_input(self):
        """Run each input line through the evaluator and show the results."""
        raw_input = self.input_text.get("1.0", tk.END)

        # Just in case; normally Process is disabled when the input is empty.
        if raw_input.strip() == "":
            messagebox.showinfo("Nothing to process", "Input area is empty.")
            return

        lines = [ln for ln in raw_input.splitlines() if ln.strip() != ""]

        entries = []
        variables_used = []
        errors = []
        variables = {}

        for i, line in enumerate(lines, start=1):
            entry = evaluate_line(line, i, variables)
            entries.append(entry)

            if entry.get("var_name") and entry["var_name"] not in variables_used:
                variables_used.append(entry["var_name"])
            if entry.get("error"):
                errors.append(entry["error"])

        output_str = build_output_text(entries, variables_used, errors)

        # Overwrite the output area.
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", output_str)
        self.output_text.config(state=tk.DISABLED)


def build_output_text(entries, variables_used, errors):
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
        output += "\n".join(variables_used) + "\n"
    else:
        output += "(none)\n"

    output += f"{separator}\n"
    output += "Errors found:\n"
    if errors:
        output += "\n".join(errors) + "\n"
    else:
        output += "(none)\n"

    return output


def evaluate_line(line, index, variables):
    """Parse, convert, and evaluate one line; updates variables in place."""
    parsed = parse_line(line)

    if parsed.kind == "invalid":
        return {
            "line": parsed.raw.strip(),
            "postfix": INVALID_MESSAGE,
            "result_line": INVALID_MESSAGE,
            "var_name": None,
            "error": f"Line {index}: {parsed.error}",
        }

    postfix = infix_to_postfix(parsed.expression)
    value, error = evaluate_postfix(postfix, variables)

    if error:
        return {
            "line": parsed.raw.strip(),
            "postfix": " ".join(postfix),
            "result_line": "error",
            "var_name": None,
            "error": f"Line {index}: {error}",
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
        "error": None,
    }


def main():
    try:
        root = tk.Tk()
        # Bring the window to the front so it's not hidden behind others.
        root.lift()
        root.attributes("-topmost", True)
        app = ExpressionEvaluatorGUI(root)
        root.after(200, lambda: root.attributes("-topmost", False))
        root.mainloop()
    except Exception as e:
        # Show the actual error instead of failing silently.
        messagebox.showerror("Error starting UI", f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
