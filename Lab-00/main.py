import tkinter as tk
from tkinter import messagebox

from gui import ExpressionEvaluatorGUI


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
