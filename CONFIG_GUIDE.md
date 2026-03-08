# Configuration Guide

## Quick Start - config.py

All application settings are now centralized in `config.py`. No need to edit multiple files!

## 🔧 Common Configuration Tasks

### 1. Enable AI-Powered Rule Extraction

Edit `config.py`:
```python
class AIConfig:
    USE_LANGCHAIN = True  # Change to True
    OPENAI_API_KEY = "sk-your-key-here"  # Add your key
    MODEL_NAME = "gpt-3.5-turbo"  # or gpt-4, gpt-4-turbo
```

**Preferred: Use environment variable**
```bash
# Windows
set OPENAI_API_KEY=sk-your-key-here

# Linux/Mac
export OPENAI_API_KEY=sk-your-key-here
```

Then in `config.py`:
```python
class AIConfig:
    USE_LANGCHAIN = True
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)  # Already set!
```

### 2. Change AI Model

```python
class AIConfig:
    MODEL_NAME = "gpt-4"  # Options: gpt-3.5-turbo, gpt-4, gpt-4-turbo
    TEMPERATURE = 0.2  # 0.0-2.0 (lower = more consistent)
    MAX_TOKENS = 2000  # Maximum response length
```

### 3. Customize AI Prompts

Edit prompt templates in `config.py`:
```python
class PromptTemplates:
    SYSTEM_PROMPT = """Your custom system prompt here..."""
    
    EXTRACTION_PROMPT_TEMPLATE = """Your custom extraction prompt...
    
    Use {document} placeholder for the document text.
    """
```

### 4. Adjust Shipping Rates

```python
class ShippingConfig:
    class FedEx:
        BASE_RATE = 6.00      # Was 5.00
        WEIGHT_RATE = 0.60    # Was 0.50 per lb
        DISTANCE_RATE = 0.12  # Was 0.10 per mile
    
    class UPS:
        BASE_RATE = 5.00
        WEIGHT_RATE = 0.60
        DISTANCE_RATE = 0.10
    
    # Priority shipping fee
    PRIORITY_FEE = 20.00  # Was 15.00
```

### 5. Change UI Settings

```python
class UIConfig:
    SERVER_PORT = 8080  # Change from default 7860
    SHARE = True  # Create public Gradio link
    THEME = "glass"  # Options: soft, default, glass, monochrome
```

### 6. Update Default Rules

```python
class BusinessRulesConfig:
    DEFAULT_RULES = [
        'age > 21 && location == "CA" -> ApplyDiscount(5)',
        'total >= 1000 -> ApplyDiscount(10)',
        'weight > 50 -> CalculateUPSShipping(50, 100)'
    ]
```

### 7. Enable Debug Mode

```python
class DebugConfig:
    VERBOSE = True  # Show handler chain progress
    LOG_RULE_EVALUATION = True  # Log each rule evaluation
    SHOW_PARSE_TREE = True  # Show expression tree structure
```

## 📋 Configuration Reference

### AIConfig
| Setting | Default | Description |
|---------|---------|-------------|
| `USE_LANGCHAIN` | `False` | Enable AI extraction |
| `MODEL_NAME` | `"gpt-3.5-turbo"` | OpenAI model to use |
| `TEMPERATURE` | `0.1` | Response randomness (0-2) |
| `MAX_TOKENS` | `2000` | Max response length |
| `OPENAI_API_KEY` | `None` | API key (use env var) |

### ShippingConfig
| Carrier | Base Rate | Weight Rate ($/lb) | Distance Rate ($/mi) |
|---------|-----------|-------------------|---------------------|
| FedEx | $5.00 | $0.50 | $0.10 |
| UPS | $4.50 | $0.55 | $0.08 |
| USPS | $3.50 | $0.45 | $0.05 |
| Priority Fee | $15.00 | - | - |

### UIConfig
| Setting | Default | Description |
|---------|---------|-------------|
| `SERVER_NAME` | `"127.0.0.1"` | Server host |
| `SERVER_PORT` | `7860` | Server port |
| `SHARE` | `False` | Create public link |
| `THEME` | `"soft"` | UI theme |

### DebugConfig
| Setting | Default | Description |
|---------|---------|-------------|
| `VERBOSE` | `True` | Print chain progress |
| `LOG_RULE_EVALUATION` | `False` | Log evaluations |
| `SHOW_PARSE_TREE` | `False` | Show tree structure |

## 🎯 Example Configurations

### Development Setup
```python
class AIConfig:
    USE_LANGCHAIN = False  # Test without AI
    
class DebugConfig:
    VERBOSE = True
    LOG_RULE_EVALUATION = True
    SHOW_PARSE_TREE = True
    
class UIConfig:
    SERVER_PORT = 7860
    SHARE = False
```

### Production Setup
```python
class AIConfig:
    USE_LANGCHAIN = True
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4"
    TEMPERATURE = 0.1
    
class DebugConfig:
    VERBOSE = False
    LOG_RULE_EVALUATION = False
    SHOW_PARSE_TREE = False
    
class UIConfig:
    SERVER_PORT = 80
    SHARE = True
```

### Demo/Testing Setup
```python
class AIConfig:
    USE_LANGCHAIN = False  # Use pattern matching
    
class BusinessRulesConfig:
    DEFAULT_RULES = [
        'age > 18 -> ApplyDiscount(10)',
        'weight <= 5 -> CalculateFedExShipping(5, 100)'
    ]
    
class UIConfig:
    SHARE = True  # Share with team
```

## 🔐 Security Best Practices

1. **Never commit API keys to git**
   ```python
   # Good
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   
   # Bad
   OPENAI_API_KEY = "sk-actual-key-here"
   ```

2. **Use .env file** (create `.env` in project root):
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```
   
   Then install python-dotenv:
   ```bash
   pip install python-dotenv
   ```
   
   Add to top of `config.py`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Add .env to .gitignore**
   ```
   .env
   *.env
   ```

## 📚 Helper Functions

Config provides convenience functions:

```python
from config import get_ai_config, get_shipping_config, get_prompt_config

# Get all AI settings as dict
ai_settings = get_ai_config()

# Get shipping rates
shipping_rates = get_shipping_config()

# Get prompts
prompts = get_prompt_config()
```

## 🆘 Troubleshooting

**Problem:** AI extraction not working
```python
# Check these in config.py:
AIConfig.USE_LANGCHAIN = True  # Must be True
AIConfig.OPENAI_API_KEY = "sk-..."  # Must be valid
# Install: pip install langchain langchain-openai openai
```

**Problem:** UI won't start
```python
# Check port isn't in use:
UIConfig.SERVER_PORT = 8080  # Try different port
```

**Problem:** Shipping prices seem wrong
```python
# Verify rates in config.py:
ShippingConfig.FedEx.BASE_RATE = 5.00
ShippingConfig.FedEx.WEIGHT_RATE = 0.50
```

**Problem:** Too much console output
```python
# Reduce verbosity:
DebugConfig.VERBOSE = False
DebugConfig.LOG_RULE_EVALUATION = False
```
