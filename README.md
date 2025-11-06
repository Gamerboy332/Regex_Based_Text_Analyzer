DFA Playground
A Deterministic Finite Automaton (DFA) Playground built with Python, Tkinter, Graphviz, and Pillow. This interactive tool allows you to define DFAs, test input strings, and visualize automaton behavior with highlighted paths. It’s designed for students, educators, and enthusiasts exploring automata theory.

✨ Features
Define DFA interactively

Enter states, alphabet, start state, final states, and transitions via dialog prompts.

Test Strings

Input a string and see whether it is Accepted or Rejected.

Traversed path is highlighted in red on the DFA diagram.

Result Window

Displays:

DFA diagram/chart with highlighted path

Result text (input string, Accepted/Rejected, path)

Save as PNG/JPG button to export the result image

OK button to close the result window

Workflow Navigation

Switch between Define DFA and Test Strings screens.

Test multiple strings without redefining the DFA.

🖼️ Example Workflow
Define DFA

States: A,B

Alphabet: 0,1

Start State: A

Final States: B

Transitions:

(A,0) → B

(A,1) → A

(B,0) → B

(B,1) → A

Test Strings

Input: 1010 → Accepted

Path: A → A → B → B → B

Diagram shows path in red.

Save result as dfa_result_1010.png / .jpg.

📦 Requirements
Python 3.8+

Graphviz (must be installed and added to PATH)

Python packages:

tkinter (usually included with Python)

pillow

graphviz

Install dependencies:

bash
pip install pillow graphviz
🚀 Usage
Run the program:

bash
python dfa_playground.py
Steps:

Click Define DFA and enter automaton details.

Switch to Test Strings screen.

Enter an input string and click Run Test.

In the result window:

View DFA diagram and result text.

Click Save as PNG/JPG to export.

Click OK to close and test another string.

🎯 Target Audience
Students learning automata theory

Educators demonstrating DFA concepts

Researchers/Enthusiasts experimenting with finite automata

📌 Notes
Diagrams are generated using Graphviz and displayed via Pillow/Tkinter.

Saved images include both the DFA diagram and the test result text.

Works cross‑platform (Windows, macOS, Linux) as long as Graphviz is installed.
