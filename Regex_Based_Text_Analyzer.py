import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog as _sd  # keep alias in case used elsewhere
from tkinter import filedialog
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import graphviz
import os
from pathlib import Path

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
        # Center & size
        self.root.geometry("900x700")
        # Dark theme palette inspired by the provided mockup
        self.COL_BG = '#0f2b44'        # deep navy background
        self.COL_PANEL = '#13324a'     # slightly lighter panels
        self.COL_CARD = '#102837'      # card background
        self.COL_ACCENT = '#31c7ff'    # cyan accent
        self.COL_TEXT = '#e6f0fb'      # pale text
        self.COL_MUTED = '#9fb6ca'
        self.root.configure(bg=self.COL_BG)
        try:
            # prefer native look; fallback to 'clam' if not available
            style = ttk.Style()
            style.theme_use('vista')
        except Exception:
            try:
                ttk.Style().theme_use('clam')
            except Exception:
                pass

        # Application fonts / style tweaks
        default_font = ("Segoe UI", 10)
        self.default_font = default_font

        # Frames (screens)
        # We'll reuse the three-column layout in both screens: left/nav, center/workspace, right/inspector
        self.define_frame = tk.Frame(root, bg=self.COL_BG)
        self.test_frame = tk.Frame(root, bg=self.COL_BG)

        # State
        self.dfa = None
        self.last_input = None
        self.last_result = None
        self.last_path = None
        self.last_img_path = None

        # UI setup
        self.setup_menu()
        self.setup_define_frame()
        self.setup_test_frame()

        # show define frame initially
        self.define_frame.pack(fill="both", expand=True)

        # status bar
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self.root, textvariable=self.status_var, bg=self.COL_PANEL, fg=self.COL_TEXT, anchor="w")
        status.pack(side="bottom", fill="x")

    def setup_define_frame(self):
        # clear
        for child in self.define_frame.winfo_children():
            child.destroy()

        # three-column layout
        container = tk.Frame(self.define_frame, bg=self.COL_BG)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(container, width=200, bg=self.COL_PANEL)
        left.pack(side="left", fill="y", padx=(0,12), pady=6)

        center = tk.Frame(container, bg=self.COL_BG)
        center.pack(side="left", fill="both", expand=True, pady=6)

        right = tk.Frame(container, width=260, bg=self.COL_PANEL)
        right.pack(side="right", fill="y", padx=(12,0), pady=6)

        # Left nav - functional
        ttk.Label(left, text="Menu", background=self.COL_PANEL, foreground=self.COL_TEXT, font=("Segoe UI", 12, "bold")).pack(pady=8, padx=8, anchor="w")
        b_home = tk.Button(left, text="Home", relief="flat", bg=self.COL_CARD, fg=self.COL_TEXT, activebackground=self.COL_ACCENT, bd=0, command=self.show_home)
        b_home.pack(fill="x", padx=8, pady=6)
        b_define = tk.Button(left, text="Define DFA", relief="flat", bg=self.COL_CARD, fg=self.COL_TEXT, activebackground=self.COL_ACCENT, bd=0, command=self.show_define_frame)
        b_define.pack(fill="x", padx=8, pady=6)
        b_load = tk.Button(left, text="Load DFA", relief="flat", bg=self.COL_CARD, fg=self.COL_TEXT, activebackground=self.COL_ACCENT, bd=0, command=self.load_dfa_from_file)
        b_load.pack(fill="x", padx=8, pady=6)
        b_examples = tk.Button(left, text="Examples", relief="flat", bg=self.COL_CARD, fg=self.COL_TEXT, activebackground=self.COL_ACCENT, bd=0, command=self.load_example_dfa)
        b_examples.pack(fill="x", padx=8, pady=6)

        # Center area: main definition controls
        header = tk.Label(center, text="Define DFA", bg=self.COL_BG, fg=self.COL_TEXT, font=("Segoe UI", 16, "bold"))
        header.pack(pady=(6,8), anchor="w")

        desc = tk.Label(center, text=("Create a DFA by entering states, alphabet, start and final states. "
                                       "Transitions can be entered manually in a compact form when you click 'Define DFA'."),
                        bg=self.COL_BG, fg=self.COL_MUTED, wraplength=520, justify="left")
        desc.pack(pady=(0,12), anchor="w")

        btn_row = tk.Frame(center, bg=self.COL_BG)
        btn_row.pack(pady=6, anchor="w")
        define_btn = tk.Button(btn_row, text="Define DFA (Form)", command=self.define_dfa, bg=self.COL_ACCENT, fg="#042033", relief="raised")
        define_btn.pack(side="left", padx=8)

        load_btn = tk.Button(btn_row, text="Load from File...", command=self.load_dfa_from_file, bg=self.COL_CARD, fg=self.COL_TEXT, relief="flat")
        load_btn.pack(side="left", padx=8)

        proceed_btn = tk.Button(btn_row, text="Proceed to Test Strings", command=self.show_test_frame, bg=self.COL_CARD, fg=self.COL_TEXT, relief="flat")
        proceed_btn.pack(side="left", padx=8)

        # Quick snapshot of current DFA (if any)
        self.dfa_summary = tk.Label(center, text="No DFA defined.", bg=self.COL_BG, fg=self.COL_TEXT, font=("Consolas", 10))
        self.dfa_summary.pack(pady=12, padx=2, anchor="w")

        # Right inspector: small preview and actions
        ttk.Label(right, text="Inspector", background=self.COL_PANEL, foreground=self.COL_TEXT, font=("Segoe UI", 12, "bold")).pack(pady=8, padx=8, anchor="w")
        self.inspector_summary = tk.Label(right, text="No DFA loaded.", bg=self.COL_PANEL, fg=self.COL_MUTED, justify="left", wraplength=220)
        self.inspector_summary.pack(padx=8, pady=6)
        ttk.Button(right, text="Open Mockup", command=lambda: self.status_var.set('Design mockup reference'),).pack(padx=8, pady=6, anchor="w")
        ttk.Button(right, text="Go to Test", command=self.show_test_frame).pack(padx=8, pady=6, anchor="w")

    def setup_test_frame(self):
        for child in self.test_frame.winfo_children():
            child.destroy()

        # three-column layout for test screen
        container = tk.Frame(self.test_frame, bg=self.COL_BG)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        left = tk.Frame(container, width=200, bg=self.COL_PANEL)
        left.pack(side="left", fill="y", padx=(0,12), pady=6)

        center = tk.Frame(container, bg=self.COL_BG)
        center.pack(side="left", fill="both", expand=True, pady=6)

        right = tk.Frame(container, width=260, bg=self.COL_PANEL)
        right.pack(side="right", fill="y", padx=(12,0), pady=6)

        # left nav
        ttk.Label(left, text="Devices", background=self.COL_PANEL, foreground=self.COL_TEXT, font=("Segoe UI", 12, "bold")).pack(pady=8, padx=8, anchor="w")
        sample_nav = ["House exterior", "Lights", "Cams", "Router", "Air conditioning"]
        for it in sample_nav:
            b = tk.Button(left, text=it, relief="flat", bg=self.COL_CARD, fg=self.COL_TEXT, command=lambda t=it: self.status_var.set(f"Selected: {t}"))
            b.pack(fill="x", padx=8, pady=6)

        # center: input and preview
        header = tk.Label(center, text="Test Strings", bg=self.COL_BG, fg=self.COL_TEXT, font=("Segoe UI", 16, "bold"))
        header.pack(pady=6, anchor="w")

        entry_row = tk.Frame(center, bg=self.COL_BG)
        entry_row.pack(pady=6, anchor="w")
        tk.Label(entry_row, text="Input:", bg=self.COL_BG, fg=self.COL_TEXT).pack(side="left")
        self.input_entry = ttk.Entry(entry_row, width=36)
        self.input_entry.pack(side="left", padx=8)
        run_btn = tk.Button(entry_row, text="Run Test", command=self.run_test, bg=self.COL_ACCENT, fg="#042033")
        run_btn.pack(side="left", padx=8)
        back_btn = tk.Button(entry_row, text="Back", command=self.show_define_frame, bg=self.COL_CARD, fg=self.COL_TEXT)
        back_btn.pack(side="left", padx=6)

        # result & preview
        self.result_label = tk.Label(center, text="No test run yet.", bg=self.COL_BG, fg=self.COL_TEXT, justify="left", font=("Consolas", 11))
        self.result_label.pack(anchor="nw", pady=8)

        self.inline_image_label = tk.Label(center, bg=self.COL_BG)
        self.inline_image_label.pack(pady=6)

        # right inspector: result actions and commands (mimic mockup inspector)
        ttk.Label(right, text="General commands", background=self.COL_PANEL, foreground=self.COL_TEXT, font=("Segoe UI", 12, "bold")).pack(pady=8, padx=8, anchor="w")
        self.inspector_result = tk.Label(right, text="No run yet.", bg=self.COL_PANEL, fg=self.COL_TEXT, wraplength=220, justify="left")
        self.inspector_result.pack(padx=8, pady=6)

        self.save_button = tk.Button(right, text="Save Result", command=self.export_current_result, bg=self.COL_ACCENT, fg="#042033")
        self.save_button.pack(padx=8, pady=8)
        self.save_button.config(state="disabled")

        # keyboard shortcuts and UX bindings
        self.bind_shortcuts()

    def show_define_frame(self):
        self.test_frame.pack_forget()
        self.define_frame.pack(fill="both", expand=True)

    def show_test_frame(self):
        if not self.dfa:
            messagebox.showinfo("Info", "Define a DFA first.")
            return
        self.define_frame.pack_forget()
        self.test_frame.pack(fill="both", expand=True)

    def define_dfa(self):
        # New modal form for defining DFA with a transitions text area
        form = tk.Toplevel(self.root)
        form.title("Define DFA")
        form.transient(self.root)
        form.grab_set()
        form.geometry("720x560")

        frm = ttk.Frame(form, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="States (comma separated):").pack(anchor="w")
        states_ent = ttk.Entry(frm)
        states_ent.pack(fill="x", pady=4)

        ttk.Label(frm, text="Alphabet symbols (comma separated):").pack(anchor="w")
        alpha_ent = ttk.Entry(frm)
        alpha_ent.pack(fill="x", pady=4)

        top_row = ttk.Frame(frm)
        top_row.pack(fill="x", pady=4)
        ttk.Label(top_row, text="Start state:").pack(side="left")
        start_ent = ttk.Entry(top_row, width=20)
        start_ent.pack(side="left", padx=8)
        ttk.Label(top_row, text="Final states (comma separated):").pack(side="left", padx=8)
        final_ent = ttk.Entry(top_row)
        final_ent.pack(side="left", padx=4, fill="x", expand=True)

        ttk.Label(frm, text="Transitions (one per line, format: src,sym->dst). Example: q0,a->q1").pack(anchor="w", pady=(12,2))
        trans_txt = tk.Text(frm, height=12)
        trans_txt.pack(fill="both", expand=True)

        note = ttk.Label(frm, text="When finished click Save. All fields are required.")
        note.pack(pady=6)

        def save_def():
            try:
                states_str = states_ent.get().strip()
                alphabet_str = alpha_ent.get().strip()
                start_state = start_ent.get().strip()
                final_states_str = final_ent.get().strip()
                trans_text = trans_txt.get("1.0", "end").strip()

                if not states_str or not alphabet_str or not start_state or not final_states_str:
                    messagebox.showerror("Error", "All DFA fields are required.")
                    return

                states = set(s.strip() for s in states_str.split(",") if s.strip())
                alphabet = set(a.strip() for a in alphabet_str.split(",") if a.strip())
                final_states = set(s.strip() for s in final_states_str.split(",") if s.strip())

                transitions = {}
                if trans_text:
                    for ln in trans_text.splitlines():
                        ln = ln.strip()
                        if not ln:
                            continue
                        # expected format: src,sym->dst
                        if '->' not in ln or ',' not in ln:
                            messagebox.showerror("Error", f"Invalid transition format: {ln}")
                            return
                        left, dst = ln.split('->', 1)
                        src, sym = left.split(',', 1)
                        transitions[(src.strip(), sym.strip())] = dst.strip()

                # basic validation: ensure transitions defined for provided symbols/states is optional
                self.dfa = DFA(states, alphabet, transitions, start_state, final_states)
                self.dfa_summary.configure(text=f"DFA with {len(states)} states, alphabet size {len(alphabet)}")
                self.status_var.set("DFA defined")
                form.destroy()
                messagebox.showinfo("Success", "DFA defined successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to define DFA:\n{e}")

        btn_row = ttk.Frame(frm)
        btn_row.pack(fill="x", pady=6)
        ttk.Button(btn_row, text="Save", command=save_def).pack(side="right", padx=6)
        ttk.Button(btn_row, text="Cancel", command=form.destroy).pack(side="right")

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

        # update UI inline
        self.result_label.configure(text=f"Input: {self.last_input}\nResult: {self.last_result}\nPath: {' -> '.join(self.last_path)}")
        self.status_var.set(f"Last run: {self.last_input} ({self.last_result})")
        # enable save
        self.save_button.state(['!disabled'])

        # Optional inline preview in test screen
        try:
            preview_img = Image.open(img_path)
            preview_img.thumbnail((760, 480))
            self._preview_tk_img = ImageTk.PhotoImage(preview_img)  # keep reference
            self.inline_image_label.configure(image=self._preview_tk_img)
        except Exception:
            # clear preview if present
            try:
                self.inline_image_label.configure(image='')
            except Exception:
                pass

        # Also open the result window for a larger view
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

        # also allow saving via menu / inline save
        self.status_var.set(f"Result ready: {self.last_input} ({self.last_result})")

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

    def export_current_result(self):
        # wrapper used by save button in test screen
        if not self.last_img_path:
            messagebox.showerror("Error", "No result to save.")
            return
        try:
            # ask for file location
            default = f"dfa_result_{self.last_input}.png" if self.last_input else "dfa_result.png"
            p = filedialog.asksaveasfilename(defaultextension='.png', initialfile=default,
                                             filetypes=[('PNG Image', '*.png'), ('JPEG', '*.jpg;*.jpeg')])
            if not p:
                return
            self.export_result_image(self.last_img_path, self.last_input, self.last_result, self.last_path, p)
            messagebox.showinfo("Saved", f"Result saved to: {os.path.abspath(p)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image:\n{e}")

    def load_dfa_from_file(self):
        # allow user to load a simple text format (same as form expectations)
        p = filedialog.askopenfilename(filetypes=[('Text', '*.txt'), ('All files', '*.*')])
        if not p:
            return
        try:
            text = Path(p).read_text(encoding='utf-8')
            # Expect a simple small format: lines starting with keywords, or a full transitions block
            # We'll try to find keys: states:, alphabet:, start:, finals:, transitions:\n...
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            data = {'states': '', 'alphabet': '', 'start': '', 'finals': '', 'transitions': []}
            mode = None
            for ln in lines:
                low = ln.lower()
                if low.startswith('states:'):
                    data['states'] = ln.split(':',1)[1].strip()
                elif low.startswith('alphabet:'):
                    data['alphabet'] = ln.split(':',1)[1].strip()
                elif low.startswith('start:'):
                    data['start'] = ln.split(':',1)[1].strip()
                elif low.startswith('finals:') or low.startswith('final states:'):
                    data['finals'] = ln.split(':',1)[1].strip()
                elif low.startswith('transitions:'):
                    mode = 'transitions'
                else:
                    if mode == 'transitions':
                        data['transitions'].append(ln)
            # Build DFA if possible
            if not data['states'] or not data['alphabet'] or not data['start']:
                messagebox.showerror('Error', 'File missing required DFA fields (states, alphabet, start)')
                return
            states = set(s.strip() for s in data['states'].split(',') if s.strip())
            alphabet = set(a.strip() for a in data['alphabet'].split(',') if a.strip())
            final_states = set(s.strip() for s in data['finals'].split(',') if s.strip())
            transitions = {}
            for ln in data['transitions']:
                if '->' in ln and ',' in ln:
                    left, dst = ln.split('->',1)
                    src, sym = left.split(',',1)
                    transitions[(src.strip(), sym.strip())] = dst.strip()
            self.dfa = DFA(states, alphabet, transitions, data['start'], final_states)
            self.dfa_summary.configure(text=f"DFA loaded from {os.path.basename(p)}")
            self.status_var.set('DFA loaded')
            messagebox.showinfo('Loaded', 'DFA loaded successfully from file')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load DFA:\n{e}')

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label='Load DFA...', command=self.load_dfa_from_file)
        filem.add_separator()
        filem.add_command(label='Exit', command=self.root.quit)
        menubar.add_cascade(label='File', menu=filem)

        helpm = tk.Menu(menubar, tearoff=0)
        def about():
            messagebox.showinfo('About', 'DFA Playground\nImproved UI')
        helpm.add_command(label='About', command=about)
        menubar.add_cascade(label='Help', menu=helpm)

        self.root.config(menu=menubar)

    def show_home(self):
        # Navigate to define frame and show a friendly welcome in the center
        self.show_define_frame()
        try:
            self.dfa_summary.configure(text=("Welcome to DFA Playground\n\nUse 'Define DFA' to create a new automaton, 'Load DFA' to import from a text file, or 'Examples' to load a sample."))
            self.status_var.set('Home')
        except Exception:
            pass

    def load_example_dfa(self):
        # Build a small example DFA (binary strings ending with '01')
        states = {'q0', 'q1', 'q2'}
        alphabet = {'0', '1'}
        transitions = {
            ('q0', '0'): 'q0', ('q0', '1'): 'q1',
            ('q1', '0'): 'q2', ('q1', '1'): 'q1',
            ('q2', '0'): 'q0', ('q2', '1'): 'q1'
        }
        start = 'q0'
        finals = {'q2'}
        self.dfa = DFA(states, alphabet, transitions, start, finals)
        self.dfa_summary.configure(text=f"Example DFA loaded: ends-with-01 (states={len(states)})")
        self.status_var.set('Example DFA loaded')

    def bind_shortcuts(self):
        # Bind common shortcuts for improved UX
        try:
            self.root.bind('<Control-s>', lambda e: self.export_current_result())
            self.root.bind('<Control-o>', lambda e: self.load_dfa_from_file())
            self.root.bind('<Control-d>', lambda e: self.define_dfa())
            # Enter in input entry runs test
            self.root.bind('<Return>', lambda e: self._enter_pressed(e))
        except Exception:
            pass

    def _enter_pressed(self, event):
        # If focus is inside the input_entry, run test; otherwise ignore
        try:
            if hasattr(self, 'input_entry') and self.root.focus_get() == self.input_entry:
                self.run_test()
        except Exception:
            pass

# --- Run the app ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DFAApp(root)
    root.mainloop()
