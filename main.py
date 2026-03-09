"""
Simple Gradio UI for Business Rules Engine.
- Manual mode: paste full ruleset text (one rule per line).
- AI mode: read txt/pdf and convert to the same rule-string list.
- Priority mode: choose how rules are sorted.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import gradio as gr

from interpreter import RuleSet
from template import BusinessRuleController, AIRuleUpdater
from config import UIConfig


class BusinessRulesApp:
    def __init__(self) -> None:
        self.raw_rules: list[str] = []
        self.ruleset = RuleSet("Business Rules")
        self.controller = BusinessRuleController(self.ruleset)

    def add_manual_rules(self, rule_blob: str, sort_mode: str):
        new_rules = self._to_rule_list(rule_blob)
        if not new_rules:
            return "No valid manual rules found.", self._raw_rules_text(), self._compiled_rules_text()

        self.raw_rules.extend(new_rules)
        self._rebuild_with_sort(sort_mode)
        return f"Added {len(new_rules)} manual rule(s).", self._raw_rules_text(), self._compiled_rules_text()

    def add_ai_rules_from_file(self, file_obj, sort_mode: str):
        if not file_obj:
            return "Please upload a .txt or .pdf file.", self._raw_rules_text(), self._compiled_rules_text()

        try:
            doc_text = self._read_file(file_obj)
            updater = AIRuleUpdater()
            extracted_rules = updater.extract_rule_strings(doc_text)
            if not extracted_rules:
                return "No valid rules found in file.", self._raw_rules_text(), self._compiled_rules_text()

            self.raw_rules.extend(extracted_rules)
            self._rebuild_with_sort(sort_mode)
            return f"Extracted {len(extracted_rules)} rule(s) from file.", self._raw_rules_text(), self._compiled_rules_text()
        except Exception as exc:
            return f"Failed to read/parse file: {exc}", self._raw_rules_text(), self._compiled_rules_text()

    def resort_rules(self, sort_mode: str):
        if not self.raw_rules:
            return "No rules to sort.", self._raw_rules_text(), self._compiled_rules_text()

        self._rebuild_with_sort(sort_mode)
        return f"Rules sorted: {sort_mode}", self._raw_rules_text(), self._compiled_rules_text()

    def clear_all(self):
        self.raw_rules = []
        self.ruleset = RuleSet("Business Rules")
        self.controller = BusinessRuleController(self.ruleset)
        return "Cleared all rules.", "", ""

    def _read_file(self, file_obj) -> str:
        file_path = file_obj.name if hasattr(
            file_obj, "name") else str(file_obj)
        suffix = Path(file_path).suffix.lower()

        if suffix == ".txt":
            return Path(file_path).read_text(encoding="utf-8")

        if suffix == ".pdf":
            try:
                import PyPDF2
            except ImportError as exc:
                raise RuntimeError(
                    "PyPDF2 is required for PDF support. Run: pip install PyPDF2") from exc

            text_parts: list[str] = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)

        raise ValueError("Unsupported file type. Use .txt or .pdf.")

    def _to_rule_list(self, text: str | None) -> list[str]:
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip() and "->" in line]

    def _rebuild_with_sort(self, sort_mode: str):
        ordered = self._sort_rules(self.raw_rules, sort_mode)
        self.ruleset = RuleSet("Business Rules")
        self.controller = BusinessRuleController(self.ruleset)
        self.controller.update_rules_manual(ordered)

    def _sort_rules(self, rules: Iterable[str], sort_mode: str) -> list[str]:
        rules = list(rules)
        if sort_mode == "Keep input order":
            return rules

        reverse = sort_mode == "Most restrictive first"
        return sorted(rules, key=self._complexity_score, reverse=reverse)

    def _complexity_score(self, rule: str) -> int:
        condition = rule.split("->", 1)[0]
        return (
            condition.count("&&") * 2
            + condition.count("||")
            + condition.count("!")
            + condition.count("(")
            + condition.count(")")
        )

    def _raw_rules_text(self) -> str:
        import re

        def strip_priority(rule: str) -> str:
            return re.sub(r"^\[P\s*=\s*\d{1,3}\]\s*", "", rule)
        return "\n".join(f"{i + 1}. {strip_priority(r)}" for i, r in enumerate(self.raw_rules))

    def _compiled_rules_text(self) -> str:
        try:
            lines = self.controller.list_rules()
            if isinstance(lines, list):
                return "\n".join(lines)
            return str(lines)
        except Exception:
            return ""

    def process_request(self, request_data: str):
        try:
            result = self.controller.process_request(request_data)
            return "Request processed successfully.", str(result)
        except Exception as exc:
            return f"Error processing request: {exc}", ""


def create_ui():
    app = BusinessRulesApp()

    theme_name = getattr(UIConfig, "THEME", "soft")
    theme_map = {
        "soft": gr.themes.Soft(),
        "default": gr.themes.Default(),
        "glass": gr.themes.Glass(),
        "monochrome": gr.themes.Monochrome(),
    }
    theme = theme_map.get(theme_name, gr.themes.Soft())

    with gr.Blocks(title="Business Rules Engine", theme=theme) as ui:
        gr.Markdown("## Business Rules Engine")
        gr.Markdown(
            "Manual: paste rules. AI: upload txt/pdf and extract rules.")

        sort_mode = gr.Dropdown(
            choices=["Most restrictive first",
                     "Keep input order", "Least restrictive first"],
            value="Most restrictive first",
            label="Priority sorting mode",
        )

        with gr.Row():
            manual_rules = gr.Textbox(
                label="Manual rules (one per line: condition -> action)",
                lines=10,
                placeholder='age > 18 && location == "NY" -> ApplyDiscount(10)',
            )
            upload_file = gr.File(
                label="Upload (.txt or .pdf)", file_types=[".txt", ".pdf"])

        with gr.Row():
            add_manual_btn = gr.Button(
                "Append Manual Rules", variant="primary")
            add_ai_btn = gr.Button("Append Rules From File")
            resort_btn = gr.Button("Re-sort Rules")
            clear_btn = gr.Button("Clear All")

        with gr.Row():
            request_data = gr.Textbox(
                label="Request data (JSON format)", lines=5, placeholder='{"age": 25, "location": "NY", "total": 600}')
        submit_request = gr.Button(
            "Submit a request to evaluate rules", variant="secondary")

        status = gr.Textbox(label="Status", interactive=False)
        raw_rules_out = gr.Textbox(
            label="Current raw rule list", lines=10, interactive=False)
        compiled_rules_out = gr.Textbox(
            label="Compiled / ordered rules", lines=10, interactive=False)

        request_results = gr.Textbox(
            label="Request processing results", lines=10, interactive=False)

        add_manual_btn.click(
            app.add_manual_rules,
            inputs=[manual_rules, sort_mode],
            outputs=[status, raw_rules_out, compiled_rules_out],
        )
        add_ai_btn.click(
            app.add_ai_rules_from_file,
            inputs=[upload_file, sort_mode],
            outputs=[status, raw_rules_out, compiled_rules_out],
        )
        resort_btn.click(
            app.resort_rules,
            inputs=[sort_mode],
            outputs=[status, raw_rules_out, compiled_rules_out],
        )
        clear_btn.click(
            app.clear_all,
            inputs=[],
            outputs=[status, raw_rules_out, compiled_rules_out],
        )

        submit_request.click(
            app.process_request,
            inputs=[request_data],
            outputs=[status, request_results],

        )

    return ui


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(
        server_name=getattr(UIConfig, "SERVER_NAME", "127.0.0.1"),
        server_port=getattr(UIConfig, "SERVER_PORT", 7860),
        share=getattr(UIConfig, "SHARE", False),
    )
