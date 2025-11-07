# DFA Playground (Web Version)

> The repository name references a previous regex/text analyzer concept. The current codebase provides a single‑page, browser‑based Deterministic Finite Automaton (DFA) playground implemented in plain HTML/CSS/JavaScript (`index.html`). No build step or external runtime dependencies are required.

## Quick Start

1. Open `index.html` in any modern browser (Chrome, Firefox, Edge, Safari).
2. Define your DFA (name, states, alphabet, start, finals, transitions).
3. Click "Save DFA" to persist it (diagram updates automatically).
4. Test an input string with "Run Test" or animate traversal with "Simulate".
5. Export / import, share, or store multiple DFAs via the Saved DFAs list.

## Core Features

| Area | Capability |
|------|------------|
| Define DFA | Enter: name (optional), states, alphabet, start state, final states, transitions (one per line: `src,symbol->dst`). |
| Random Generator | "Create Random" button builds a complete deterministic DFA by assigning a random destination for every (state, symbol). |
| Saved DFAs | Automatic localStorage list with Load/Delete controls; dedupes identical DFAs; keeps up to 30 entries. |
| Persistence | The most recently defined DFA is auto‑persisted to localStorage (`dfa_saved`). |
| History Log | Records only tested input strings and their Accepted/Rejected result (color coded green/red). |
| Simulation | Step‐by‐step animated traversal shows incremental path progression. |
| Diagram Rendering | Custom SVG: circular layout, self‑loops, grouped multi‑symbol edges, parallel offset for reverse direction edges, highlighted path in red. |
| Export | PNG/JPG (diagram + test summary), JSON, TXT (plain text format). |
| Import | Load JSON or TXT to populate the form and re‑persist/save. |
| Share Link | One‑click link generation: DFA serialized, base64 encoded in URL hash (`#dfa=...`), including name. |
| Renaming | DFA name stored with saved entries and restored on load/share. |
| Status & Inspector | Live status updates and a compact inspector panel summarizing DFA metrics. |

## UI Sections

Left Column: Status, Inspector, Saved DFAs list.
Center Column: Define DFA form, Test Strings panel, Diagram Preview.
Right Column: Result panel (save image buttons), Examples loader, History log.

## Examples

Two built‑in examples:

1. Ends with `01`
2. Simple two‑state A/B DFA

Selecting an example populates the form, assigns a name, saves & renders automatically.

## Transition Format (Manual Entry)

Each transition line: `source,symbol->destination`

Example:
```
q0,0->q0
q0,1->q1
q1,0->q2
q1,1->q1
q2,0->q0
q2,1->q1
```

Deterministic requirement: At most one destination per (state, symbol). The random generator creates a complete mapping (exactly one per pair).

## TXT Import / Export Format

```
states: q0,q1,q2
alphabet: 0,1
start: q0
finals: q2
transitions:
q0,0->q0
q0,1->q1
q1,0->q2
q1,1->q1
q2,0->q0
q2,1->q1
```

Lines are trimmed; case is not enforced. Everything after `transitions:` is treated as transition lines until EOF.

## JSON Export Structure

```
{
	"states": ["q0","q1","q2"],
	"alphabet": ["0","1"],
	"start": "q0",
	"finals": ["q2"],
	"transitions": [
		{"src":"q0","sym":"0","dst":"q0"},
		{"src":"q0","sym":"1","dst":"q1"},
		{"src":"q1","sym":"0","dst":"q2"},
		{"src":"q1","sym":"1","dst":"q1"},
		{"src":"q2","sym":"0","dst":"q0"},
		{"src":"q2","sym":"1","dst":"q1"}
	]
}
```

Import expects the same shape. Invalid JSON triggers an alert.

## Share Links

Share links embed a base64‑encoded JSON object (including name) in the URL hash. Opening the link auto‑loads the DFA if decoding succeeds:

`https://your-host/index.html#dfa=<encoded>`

No server required: Everything runs client‑side.

## Local Storage Keys

| Key | Purpose |
|-----|---------|
| `dfa_saved` | Last active DFA (including name). |
| `dfa_saved_list` | Array of saved DFA entries (each: id, name, sig, data). |

Clearing browser storage removes persistence.

## Image Export Details

When saving PNG/JPG:
- Diagram rendered from current SVG.
- Test input and result stamped beneath the image.
- JPG gets a white background; PNG stays transparent.

## History Behavior

Only input test attempts are logged. Log shows: `inputString — Accepted/Rejected` with color coding. Simulation also logs final result.

## Styling

Enhanced button styling (.btn, .btn-ghost, .secondary) for clearer affordance and theme consistency (hover elevation, disabled states). Colors derive from CSS custom properties at the top of `index.html`.

## Limitations / Future Ideas

| Area | Potential Improvement |
|------|-----------------------|
| Validation | Surface warnings for missing transitions (incomplete DFA). |
| Minimization | Add optional DFA minimization button. |
| NFA Support | Extend parser & renderer for nondeterministic automata. |
| Bulk Actions | Multi‑delete in Saved DFAs list. |
| Export Name | Include `name` field in JSON/TXT explicitly (currently excluded from TXT & JSON export for compatibility). |

## Contributing

Open a PR or issue with ideas—this is a single‑file prototype intentionally kept lightweight.

## Acknowledgements

Automata theory concepts are standard; implementation and UI are custom. Original repository name retained for continuity.

---
Enjoy exploring DFAs in the browser!