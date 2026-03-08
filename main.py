"""
Main Gradio UI for Business Rules Engine
Supports manual rule entry and AI-powered document extraction
"""

import gradio as gr
from interpreter import RuleSet
from template import BusinessRuleController
from context import Context
from config import UIConfig, AIConfig
import json


class BusinessRulesApp:
    def __init__(self):
        self.controller = None
        self.ruleset = None
        self.reset_rules()
    
    def reset_rules(self):
        """Initialize a fresh ruleset"""
        self.ruleset = RuleSet("Business Rules")
        self.controller = BusinessRuleController(self.ruleset)
    
    def add_manual_rules(self, rule_text):
        """Add rules from manual text input"""
        if not rule_text or not rule_text.strip():
            return "❌ Error: Please enter at least one rule", self.get_current_rules()
        
        try:
            self.controller.update_rules_manual(rule_text)
            rule_list = self.get_current_rules()
            return f"✅ Successfully added {len(self.ruleset.rules)} rule(s)", rule_list
        except Exception as e:
            return f"❌ Error: {str(e)}", self.get_current_rules()
    
    def add_ai_rules(self, file, ai_prompt_context):
        """Extract rules from uploaded document using AI"""
        if file is None:
            return "❌ Error: Please upload a document", self.get_current_rules()
        
        try:
            # Read file content
            file_content = self._read_file(file)
            
            if not file_content:
                return "❌ Error: Could not read file content", self.get_current_rules()
            
            # For now, we'll simulate AI extraction with a simple parser
            # In production, this would call your AI service
            extracted_rules = self._simulate_ai_extraction(file_content, ai_prompt_context)
            
            if not extracted_rules:
                return "❌ Error: No rules found in document", self.get_current_rules()
            
            self.controller.update_rules_ai(extracted_rules)
            rule_list = self.get_current_rules()
            return f"✅ Successfully extracted {len(self.ruleset.rules)} rule(s) from document", rule_list
        
        except Exception as e:
            return f"❌ Error: {str(e)}", self.get_current_rules()
    
    def _read_file(self, file):
        """Read content from txt or pdf file"""
        file_path = file.name if hasattr(file, 'name') else str(file)
        
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.endswith('.pdf'):
                # Try to import PyPDF2, fallback gracefully
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    return "Error: PyPDF2 not installed. Run: pip install PyPDF2"
            
            else:
                return "Error: Unsupported file format. Use .txt or .pdf"
        
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _simulate_ai_extraction(self, document_text, context_hint):
        """
        Simulate AI extraction. In production, replace with actual AI API call.
        For demo purposes, looks for patterns like:
        - "if X then Y"
        - "when X, apply Y"
        """
        lines = document_text.split('\n')
        extracted_rules = []
        
        for line in lines:
            line = line.strip()
            # If line already looks like a formatted rule, use it
            if '->' in line:
                extracted_rules.append(line)
        
        # If we found formatted rules, return them
        if extracted_rules:
            return '\n'.join(extracted_rules)
        
        # Otherwise, return a sample based on context
        # In production, this would be your AI API call
        return """# AI-Extracted Rules (Sample - Replace with real AI integration)
# Original document was analyzed. Here are sample rules:
age > 18 && location == "NY" -> ApplyDiscount(10)
total >= 500 -> ApplyDiscount(5)"""
    
    def test_rules(self, test_data_json):
        """Test current rules with provided context data"""
        if not self.ruleset.rules:
            return "❌ No rules loaded. Please add rules first."
        
        if not test_data_json or not test_data_json.strip():
            return "❌ Please provide test data in JSON format"
        
        try:
            # Parse JSON input
            test_data = json.loads(test_data_json)
            
            # Process request
            result = self.controller.process_request(test_data)
            
            # Format output
            output = f"🔍 Test Results\n"
            output += f"Input Data: {json.dumps(test_data, indent=2)}\n\n"
            output += f"Applied Rules:\n"
            
            if isinstance(result, list):
                for rule in result:
                    output += f"  ✓ {rule}\n"
            else:
                output += f"  {result}\n"
            
            return output
        
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON format: {str(e)}"
        except Exception as e:
            return f"❌ Error processing rules: {str(e)}"
    
    def get_current_rules(self):
        """Get formatted list of current rules"""
        if not self.ruleset.rules:
            return "No rules loaded yet."
        
        rule_list = self.controller.list_rules()
        return "\n".join(rule_list)
    
    def clear_all_rules(self):
        """Clear all rules and reset"""
        self.reset_rules()
        return "✅ All rules cleared", "No rules loaded yet."


def create_ui():
    """Create and configure the Gradio interface"""
    app = BusinessRulesApp()
    
    # Determine theme
    theme_map = {
        "soft": gr.themes.Soft(),
        "default": gr.themes.Default(),
        "glass": gr.themes.Glass(),
        "monochrome": gr.themes.Monochrome()
    }
    selected_theme = theme_map.get(UIConfig.THEME, gr.themes.Soft())
    
    with gr.Blocks(title="Business Rules Engine", theme=selected_theme) as interface:
        gr.Markdown("# 🎯 Business Rules Engine")
        gr.Markdown("Add rules manually or extract them from documents using AI")
        
        # Current Rules Display (shared across tabs)
        with gr.Row():
            with gr.Column():
                rules_display = gr.Textbox(
                    label="📋 Current Rules",
                    value="No rules loaded yet.",
                    lines=8,
                    interactive=False
                )
        
        with gr.Tabs():
            # Tab 1: Manual Rule Entry
            with gr.Tab("✍️ Manual Entry"):
                gr.Markdown("""
                ### Enter Rules Manually
                Format: `condition -> action`
                
                **Discount Examples:**
                - `age > 18 && location == "NY" -> ApplyDiscount(10)`
                - `total >= 500 -> ApplyDiscount(5)`
                - `age > 65 -> ApplyDiscount(15)`
                
                **Shipping Examples:**
                - `weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)`
                - `weight > 10 -> CalculateUPSShipping(12, 250)`
                - `weight <= 2 -> CalculateUSPSShipping(1.5, 50)`
                - `order_value > 500 -> SetPriorityShipping()`
                
                Multiple rules: one per line
                """)
                
                manual_input = gr.Textbox(
                    label="Rule Text",
                    placeholder=UIConfig.MANUAL_ENTRY_PLACEHOLDER,
                    lines=8
                )
                
                manual_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Row():
                    manual_add_btn = gr.Button("➕ Add Rules", variant="primary")
                    manual_clear_btn = gr.Button("🗑️ Clear All Rules", variant="secondary")
            
            # Tab 2: AI Document Extraction
            with gr.Tab("🤖 AI Extraction"):
                gr.Markdown("""
                ### Extract Rules from Documents
                Upload a `.txt` or `.pdf` document containing business rules in natural language.
                The AI will extract and format them automatically.
                
                **Handles multiple scenarios:**
                - Discount calculations (retail, wholesale, promotional)
                - Shipping charges (FedEx, UPS, USPS)
                - Priority/express shipping rules
                
                **AI Integration:**
                - Enable Langchain in `template.py` for OpenAI/Claude integration
                - Or use the built-in pattern-based extractor
                - Gracefully falls back if AI is unavailable
                
                **Try:** Upload `sample_rules.txt` to see it in action!
                """)
                
                file_input = gr.File(
                    label="Upload Document",
                    file_types=[".txt", ".pdf"]
                )
                
                ai_context = gr.Textbox(
                    label="Additional Context (Optional)",
                    placeholder="e.g., 'These are discount rules for retail customers'",
                    lines=2
                )
                
                ai_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Row():
                    ai_extract_btn = gr.Button("🔍 Extract Rules", variant="primary")
                    ai_clear_btn = gr.Button("🗑️ Clear All Rules", variant="secondary")
            
            # Tab 3: Test Rules
            with gr.Tab("🧪 Test Rules"):
                gr.Markdown("""
                ### Test Your Rules
                Provide test data in JSON format to see which rules apply.
                
                **Discount Test:**
                ```json
                {"age": 25, "location": "NY", "total": 600}
                ```
                
                **Shipping Test:**
                ```json
                {"weight": 4.5, "distance": 80, "order_value": 550}
                ```
                
                **Combined Test:**
                ```json
                {"age": 70, "location": "NY", "total": 600, 
                 "weight": 3, "distance": 50}
                ```
                """)
                
                test_input = gr.Textbox(
                    label="Test Data (JSON)",
                    placeholder=UIConfig.TEST_DATA_PLACEHOLDER,
                    lines=8
                )
                
                test_output = gr.Textbox(
                    label="Test Results",
                    lines=10,
                    interactive=False
                )
                
                test_btn = gr.Button("▶️ Run Test", variant="primary")
        
        # Event Handlers
        manual_add_btn.click(
            fn=app.add_manual_rules,
            inputs=[manual_input],
            outputs=[manual_status, rules_display]
        )
        
        manual_clear_btn.click(
            fn=app.clear_all_rules,
            inputs=[],
            outputs=[manual_status, rules_display]
        )
        
        ai_extract_btn.click(
            fn=app.add_ai_rules,
            inputs=[file_input, ai_context],
            outputs=[ai_status, rules_display]
        )
        
        ai_clear_btn.click(
            fn=app.clear_all_rules,
            inputs=[],
            outputs=[ai_status, rules_display]
        )
        
        test_btn.click(
            fn=app.test_rules,
            inputs=[test_input],
            outputs=[test_output]
        )
        
        # Footer
        gr.Markdown(f"""
        ---
        **Design Patterns Used:** Template Method, Chain of Responsibility, Command, Interpreter
        
        **AI Status:** {'✅ Enabled' if AIConfig.USE_LANGCHAIN else '⚠️ Disabled'} (Model: {AIConfig.MODEL_NAME if AIConfig.USE_LANGCHAIN else 'N/A'})
        """)
    
    return interface


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(
        server_name=UIConfig.SERVER_NAME,
        server_port=UIConfig.SERVER_PORT,
        share=UIConfig.SHARE
    )
