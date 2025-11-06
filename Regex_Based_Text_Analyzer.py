import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import graphviz
import os

class DFA:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def process(self, input_string):
        current_state = self.start_state
        path = [current_state]
        for symbol in input_string:
            if (current_state, symbol) in self.transitions:
                current_state = self.transitions[(current_state, symbol)]
                path.append(current_state)
            else:
                return False, path
        return current_state in self.final_states, path

    def visualize(self, input_string, filename="dfa", fmt="png"):
        # Render DFA diagram and highlight path
        f = graphviz.Digraph('dfa', filename=filename, format=fmt)

        # Start arrow (phantom node)
        f.node('', shape='none', width='0', height='0')
        f.edge('', str(self.start_state))

        # States
        for state in self.states:
            shape = 'doublecircle' if state in self.final_states else 'circle'
            f.node(str(state), shape=shape)

        # Compute path
        accepted, path = self.process(input_string)

        # Transitions (highlight if in path)
        for (state, symbol), target in self.transitions.items():
            if self._edge_in_path(state, target, path):
                f.edge(str(state), str(target), label=symbol, color="red", penwidth="2")
            else:
                f.edge(str(state), str(target), label=symbol)

        output_path = f.render(view=False)
        # graphviz returns file path without extension sometimes; ensure .png
        img_path = output_path if output_path.endswith(".png") else output_path + ".png"
        return accepted, path, img_path

    def _edge_in_path(self, src, dst, path):
        for i in range(len(path)-1):
            if path[i] == src and path[i+1] == dst:
                return True
        return False


class DFAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DFA Playground")

        # Frames (screens)
        self.define_frame = tk.Frame(root)
        self.test_frame = tk.Frame(root)

        # State
        self.dfa = None
        self.last_input = None
        self.last_result = None
        self.last_path = None
        self.last_img_path = None

        # UI setup
        self.setup_define_frame()
        self.setup_test_frame()

        self.define_frame.pack(fill="both", expand=True)

    def setup_define_frame(self):
        header = tk.Label(self.define_frame, text="Define DFA", font=("Arial", 14, "bold"))
        header.pack(pady=10)

        tk.Button(self.define_frame, text="Define DFA", command=self.define_dfa).pack(pady=5)
        tk.Button(self.define_frame, text="Proceed to Test Strings", command=self.show_test_frame).pack(pady=5)

    def setup_test_frame(self):
        header = tk.Label(self.test_frame, text="Test Strings", font=("Arial", 14, "bold"))
        header.pack(pady=10)

        entry_row = tk.Frame(self.test_frame)
        entry_row.pack(pady=5)
        tk.Label(entry_row, text="Input:").pack(side="left")
        self.input_entry = tk.Entry(entry_row, width=30)
        self.input_entry.pack(side="left", padx=5)

        btn_row = tk.Frame(self.test_frame)
        btn_row.pack(pady=5)
        tk.Button(btn_row, text="Run Test", command=self.run_test).pack(side="left", padx=5)
        tk.Button(btn_row, text="Back to Define DFA", command=self.show_define_frame).pack(side="left", padx=5)

        # Placeholder for inline preview in the test screen (optional)
        self.inline_image_label = tk.Label(self.test_frame)
        self.inline_image_label.pack(pady=10)

    def show_define_frame(self):
        self.test_frame.pack_forget()
        self.define_frame.pack(fill="both", expand=True)

    def show_test_frame(self):
        if not self.dfa:
            messagebox.showinfo("Info", "Define a DFA first.")
        self.define_frame.pack_forget()
        self.test_frame.pack(fill="both", expand=True)

    def define_dfa(self):
        try:
            states_str = simpledialog.askstring("DFA", "Enter states (comma separated):")
            alphabet_str = simpledialog.askstring("DFA", "Enter alphabet symbols (comma separated):")
            start_state = simpledialog.askstring("DFA", "Enter start state:").strip()
            final_states_str = simpledialog.askstring("DFA", "Enter final states (comma separated):")

            if not states_str or not alphabet_str or not start_state or not final_states_str:
                messagebox.showerror("Error", "All DFA fields are required.")
                return

            states = set(s.strip() for s in states_str.split(",") if s.strip())
            alphabet = set(a.strip() for a in alphabet_str.split(",") if a.strip())
            final_states = set(s.strip() for s in final_states_str.split(",") if s.strip())

            transitions = {}
            for state in states:
                for symbol in alphabet:
                    target = simpledialog.askstring("Transition", f"Transition from ({state}, {symbol}):")
                    if target is None or not target.strip():
                        messagebox.showerror("Error", f"Missing transition for ({state}, {symbol}).")
                        return
                    transitions[(state.strip(), symbol.strip())] = target.strip()

            self.dfa = DFA(states, alphabet, transitions, start_state, final_states)
            messagebox.showinfo("Success", "DFA defined successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to define DFA:\n{e}")

    def run_test(self):
        if not self.dfa:
            messagebox.showerror("Error", "Define DFA first!")
            return

        input_string = self.input_entry.get().strip()
        if not input_string:
            messagebox.showerror("Error", "Enter an input string!")
            return

        try:
            accepted, path, img_path = self.dfa.visualize(input_string)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to render diagram:\n{e}")
            return

        result = "Accepted" if accepted else "Rejected"

        # Save last test info
        self.last_input = input_string
        self.last_result = result
        self.last_path = path
        self.last_img_path = img_path

        # Optional inline preview in test screen
        try:
            preview_img = Image.open(img_path)
            preview_img = preview_img.resize((500, 400))
            self._preview_tk_img = ImageTk.PhotoImage(preview_img)  # keep reference
            self.inline_image_label.configure(image=self._preview_tk_img)
        except Exception:
            pass  # If preview fails, still show the result window

        # Open dedicated result window (no blocking messagebox)
        self.open_result_window()

    def open_result_window(self):
        # Create a new result window with a clear layout
        result_win = tk.Toplevel(self.root)
        result_win.title("Test Result")
        result_win.geometry("720x640")  # give enough space

        # Top: result text
        top_frame = tk.Frame(result_win)
        top_frame.pack(fill="x", padx=12, pady=8)
        text = f"Input: {self.last_input}\nResult: {self.last_result}\nPath: {' -> '.join(self.last_path)}"
        tk.Label(top_frame, text=text, justify="left", font=("Consolas", 11)).pack(anchor="w")

        # Middle: diagram image
        mid_frame = tk.Frame(result_win)
        mid_frame.pack(fill="both", expand=True, padx=12, pady=8)
        try:
            img = Image.open(self.last_img_path)
            # Fit image to window width while keeping aspect
            max_w, max_h = 680, 440
            img.thumbnail((max_w, max_h))
            tk_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(mid_frame, image=tk_img, borderwidth=1, relief="solid")
            img_label.image = tk_img  # keep reference
            img_label.pack(pady=6)
        except Exception as e:
            tk.Label(mid_frame, text=f"(Failed to load image: {e})", fg="red").pack()

        # Bottom: action buttons
        bottom_frame = tk.Frame(result_win)
        bottom_frame.pack(fill="x", padx=12, pady=12)

        def save_action():
            try:
                png_path = f"dfa_result_{self.last_input}.png"
                jpg_path = f"dfa_result_{self.last_input}.jpg"
                self.export_result_image(self.last_img_path, self.last_input, self.last_result, self.last_path, png_path)
                self.export_result_image(self.last_img_path, self.last_input, self.last_result, self.last_path, jpg_path)
                messagebox.showinfo("Saved", f"Results saved as:\n{os.path.abspath(png_path)}\n{os.path.abspath(jpg_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save images:\n{e}")

        save_btn = tk.Button(bottom_frame, text="Save as PNG/JPG", command=save_action)
        ok_btn = tk.Button(bottom_frame, text="OK", command=result_win.destroy)

        save_btn.pack(side="left", padx=6)
        ok_btn.pack(side="right", padx=6)

    def export_result_image(self, diagram_path, input_string, result, path, export_path):
        img = Image.open(diagram_path).convert("RGBA")
        # Add a white strip at bottom with text
        padding_h = 110
        new_img = Image.new("RGBA", (img.width, img.height + padding_h), "white")
        new_img.paste(img, (0, 0))

        draw = ImageDraw.Draw(new_img)
        font = ImageFont.load_default()
        text = f"Input: {input_string}\nResult: {result}\nPath: {' -> '.join(path)}"
        draw.text((10, img.height + 10), text, fill="black", font=font)

        # Save as requested extension; convert to RGB for JPG
        if export_path.lower().endswith(".jpg") or export_path.lower().endswith(".jpeg"):
            new_img = new_img.convert("RGB")
        new_img.save(export_path)

# --- Run the app ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DFAApp(root)
    root.mainloop()
