# Business Rules Engine - Gradio UI

## ⚙️ Quick Configuration

**All settings are now in one place: `config.py`**

- Enable AI extraction: `AIConfig.USE_LANGCHAIN = True`
- Change model: `AIConfig.MODEL_NAME = "gpt-4"`
- Adjust shipping rates: `ShippingConfig.FedEx.BASE_RATE = 6.00`
- Modify prompts: `PromptTemplates.SYSTEM_PROMPT = "..."`
- UI settings: `UIConfig.SERVER_PORT = 8080`

📖 **See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for complete configuration documentation**

## Overview
This application implements an AI-Powered Business Rule Engine with a user-friendly Gradio interface. It uses multiple design patterns including Template Method, Chain of Responsibility, Command, and Interpreter patterns.

## Features
- ✍️ **Manual Rule Entry**: Directly input rules in structured format
- 🤖 **AI Document Extraction**: Upload documents (txt, pdf) to extract rules automatically using Langchain
- 🧪 **Rule Testing**: Test rules with sample data
- 📋 **Rule Management**: View and manage all loaded rules
- 💰 **Discount Rules**: Calculate retail discounts based on customer attributes
- 📦 **Shipping Rules**: Calculate shipping charges for FedEx, UPS, and USPS
- 🚀 **Priority Shipping**: Automatically upgrade eligible orders

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or with uv:
```bash
uv pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

Or with uv:
```bash
uv run main.py
```

The application will start a local server at `http://127.0.0.1:7860`

## Usage

### Manual Rule Entry
1. Navigate to the "✍️ Manual Entry" tab
2. Enter rules in the format: `condition -> action`
   - **Discount:** `age > 18 && location == "NY" -> ApplyDiscount(10)`
   - **Shipping:** `weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)`
3. Click "➕ Add Rules"
4. View loaded rules in the "Current Rules" section

### AI Document Extraction
1. Navigate to the "🤖 AI Extraction" tab
2. Upload a `.txt` or `.pdf` document containing business rules in natural language
3. Optionally provide context to help with extraction
4. Click "🔍 Extract Rules"
5. View extracted rules in the "Current Rules" section

**AI Integration Options:**
- **Langchain + OpenAI**: Set `use_langchain=True` and provide `api_key` in `template.py`
- **Custom AI Client**: Provide your own AI client with a `generate()` method
- **Pattern-based**: Falls back to pattern matching if AI is unavailable

### Testing Rules
1. Navigate to the "🧪 Test Rules" tab
2. Enter test data in JSON format:
   
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
   {"age": 70, "total": 600, "weight": 3, "distance": 50}
   ```

3. Click "▶️ Run Test"
4.**Discounts**: `ApplyDiscount(percentage)` - e.g., `ApplyDiscount(10)` for 10% off
- **FedEx Shipping**: `CalculateFedExShipping(weight, distance)` - e.g., `CalculateFedExShipping(5, 100)`
- **UPS Shipping**: `CalculateUPSShipping(weight, distance)` - e.g., `CalculateUPSShipping(12, 250)`
- **USPS Shipping**: `CalculateUSPSShipping(weight, distance)` - e.g., `CalculateUSPSShipping(2, 50)`
- **Priority Shipping**: `SetPriorityShipping()` - enables express shipping

**Adding New Actions:**
1. Create a new command class in `action.py` that extends `ActionCommand`
2. Decorate it with `@ActionCommand.register`
3. Implement `execute(self, context)` and `__str__()` methods
4. No changes needed in handlers - fully extensible== "NY"`, `total >= 500`
- Combined with AND: `age > 18 && location == "NY"`
- Combined with OR: `age > 18 || age < 65`
- Operators: `==`, `!=`, `>`, `<`, `>=`, `<=`

**Actions:**
- Currently supported: `ApplyDiscount(percentage)`
- Example: `ApplyDiscount(10)` for 10% discount

**Adding New Actions:**
1. Create a new command class in `action.py` that extends `ActionCommand`
2. Decorate it with `@ActionCommand.register`
3. Implement `execute(self, context)` and `__str__()` methods
4. No changes needed in handlers!

## Architecture

```
main.py                  → Gradio UI application
template.py              → Template Method pattern (RuleUpdater, BusinessRuleController)
handler.py               → Chain of Responsibility (extraction, normalization, ranking, parsing)
action.py                → Command pattern (ActionCommand, registry)
interpreter.py           → Interpreter pattern (Expression tree, BusinessRule, RuleSet)
parseTree.py             → Parse tree generation
context.py               → Context data container
```

## Design Patterns Used

1. **Template Method** (`template.py`): Defines algorithm skeleton for rule updates
2. **Chain of Responsibility** (`handler.py`): Sequential rule processing pipeline
3. **Command** (`action.py`): Encapsulates rule actions
4. **Interpreter** (`interpreter.py`): Evaluates condition expressions
5. **Factory/Registry** (`action.py`): Dynamic command creation from text

## Sample Files
- `sample_rules.txt`: Example business rules document for testing AI extraction

## Testing

Test the manual flow:
```bash
uv run handler.py
```

Test with the UI:
```bash
uv run main.py
```

## Requirements
- Python 3 AI Integration:
  - langchain>=0.1.0 & langchain-openai>=1.0.0 (for OpenAI)
  - openai>=1.0.0 (API client
- gradio>=4.0.0
- PyPDF2>=3.0.0 (for PDF document support)
- Optional: AI integration libraries (langchain, openai, etc.)
