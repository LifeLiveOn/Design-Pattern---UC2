# Business Rules Engine

A rule-based engine that evaluates conditions against request data and returns matching actions. Built with Gradio UI, using Template Method, Chain of Responsibility, Command, and Interpreter design patterns.

## Setup

From the project root (`Spring2026/`):

```bash
uv sync
```

## Run

```bash
cd DesignPattern/UC2/Design-Pattern---UC2
uv run main.py
```

Open `http://127.0.0.1:7860` in your browser.

## How to Use

### 1. Add Rules

Paste rules in the **Manual rules** textbox (one per line):

```
age > 65 -> ApplyDiscount(15)
age > 18 && location == "NY" -> ApplyDiscount(10)
total >= 500 -> ApplyDiscount(5)
weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)
weight > 10 && distance > 200 -> CalculateUPSShipping(12, 250)
order_value > 500 -> SetPriorityShipping()
```

Click **Append Manual Rules**.

Or upload a `.txt` / `.pdf` file and click **Append Rules From File** to extract rules via AI (Ollama).

### 2. Submit a Request

Enter JSON in the **Request data** field:

```json
{ "age": 67, "location": "NY" }
```

Click **Submit a request to evaluate rules**.

The engine evaluates every rule against your data and returns the actions whose conditions match:

```
rule_1: ApplyDiscount(15)
rule_2: ApplyDiscount(10)
```

Rules referencing keys not in your request (e.g. `total`, `weight`) are skipped.

### Rule Format

```
[P=<priority>] condition -> action
```

- **Priority** `[P=0..100]` is optional. Higher = evaluated first.
- **Conditions**: `age > 18`, `location == "NY"`, combined with `&&` (AND) / `||` (OR).
- **Actions**: any text after `->` is stored as-is (e.g. `ApplyDiscount(10)`, `special handling`).

### AI Extraction

Upload a document with unstructured business rules. The engine uses Ollama (`granite4:3b` by default) via Langchain to extract structured rules. Configure the model in `config.py` (`AIConfig.MODEL_NAME`).

Requires Ollama running locally on port 11434.

## Run Tests

```bash
uv run test_integration.py
```

## Architecture

| File             | Pattern                 | Purpose                                        |
| ---------------- | ----------------------- | ---------------------------------------------- |
| `main.py`        | —                       | Gradio UI                                      |
| `template.py`    | Template Method         | Rule update flow (Manual / AI)                 |
| `handler.py`     | Chain of Responsibility | Extract → Normalize → Rank → Parse             |
| `action.py`      | Command                 | Stores action as string via `execute()`        |
| `interpreter.py` | Interpreter             | Expression tree, rule evaluation               |
| `parseTree.py`   | —                       | Converts condition strings to expression trees |
| `context.py`     | —                       | Wraps request data dict                        |
| `config.py`      | —                       | All settings (AI model, prompts, UI)           |

## Parse Tree Visualization

Each compiled `BusinessRule` now keeps a `parse_tree` object (`rule.parse_tree`).

### 1) ASCII tree (terminal)

```python
from handler import pipeline

rules = pipeline.handle('age > 18 && location == "NY" -> ApplyDiscount(10)')
print(rules[0].parse_tree.to_ascii())
```

Example output:

```text
ParseTree<...>: age > 18 && location == "NY"
└── AND [a1b2c3d4]
	├── ATOMIC: age > 18 [e5f6a7b8]
	└── ATOMIC: location == NY [c9d0e1f2]
```

### 2) Mermaid diagram

```python
mermaid_text = rules[0].parse_tree.to_mermaid()
print(mermaid_text)
```

Use the printed Mermaid text in any Mermaid renderer.
