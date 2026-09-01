import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from processor import build_output_text, process_lines


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
            filetypes=[("Input files", "*.in")],
        )
        if not file_path:
            return  # user cancelled

        if not file_path.lower().endswith(".in"):
            messagebox.showerror("Invalid file", "Please select a file with a .in extension.")
            return

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

        entries, variables_used, errors, variables = process_lines(lines)
        output_str = build_output_text(entries, variables_used, errors, variables)

        # Overwrite the output area.
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", output_str)
        self.output_text.config(state=tk.DISABLED)
