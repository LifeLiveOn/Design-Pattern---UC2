"""
Centralized configuration for Business Rules Engine
All model settings, prompts, and parameters in one place
"""

import os

# =============================================================================
# AI MODEL CONFIGURATION
# =============================================================================

class AIConfig:
    """AI model and API settings"""
    
    # Enable/disable AI features
    USE_LANGCHAIN = False  # Set to True when you have API key configured
    
    # Model selection
    MODEL_NAME = "gpt-3.5-turbo"  # Options: gpt-3.5-turbo, gpt-4, gpt-4-turbo
    TEMPERATURE = 0.1  # Lower = more deterministic, Higher = more creative
    
    # API Keys (recommended: set via environment variables)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
    # ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", None)
    
    # Alternative: Set directly (not recommended for production)
    # OPENAI_API_KEY = "sk-..."
    
    # Langchain settings
    MAX_TOKENS = 2000
    TOP_P = 1.0


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

class PromptTemplates:
    """AI prompt templates for rule extraction"""
    
    SYSTEM_PROMPT = """You are a business rule extraction expert.
Extract ALL business rules and format each rule exactly as:
[P=<0-100>] condition -> action

Priority meaning:
- Higher P means higher priority (more restrictive/specific should usually be higher)
- P=100 is highest, P=0 is lowest

ACTIONS: ApplyDiscount(%), CalculateFedExShipping(weight, distance), 
CalculateUPSShipping(weight, distance), CalculateUSPSShipping(weight, distance), 
SetPriorityShipping()

CONDITIONS: Use ==, !=, >, <, >=, <=, && (AND), || (OR)
Quote strings, not numbers.

Output ONLY formatted rules, one per line. No explanations."""

    EXTRACTION_PROMPT_TEMPLATE = """Extract business rules from the following document.
Convert each rule to the format: [P=<0-100>] condition -> action

You must assign a priority P for each rule:
- Higher P = more restrictive/specific rule
- Lower P = broader/default rule
- Use integers only, from 0 to 100

SUPPORTED ACTIONS:
1. ApplyDiscount(percentage) - Discount calculation
    Example: [P=90] age > 65 -> ApplyDiscount(15)

2. CalculateFedExShipping(weight, distance) - FedEx shipping charges
    Example: [P=80] weight <= 5 && distance < 100 -> CalculateFedExShipping(4.5, 80)

3. CalculateUPSShipping(weight, distance) - UPS shipping charges
    Example: [P=60] weight > 10 -> CalculateUPSShipping(12, 250)

4. CalculateUSPSShipping(weight, distance) - USPS shipping charges
    Example: [P=75] weight <= 2 -> CalculateUSPSShipping(1.5, 50)

5. SetPriorityShipping() - Enable priority shipping
    Example: [P=70] order_value > 500 -> SetPriorityShipping()

CONDITION FORMAT:
- Use operators: ==, !=, >, <, >=, <=
- Combine with && (AND) or || (OR)
- Quote strings: location == "NY"
- Numbers unquoted: age > 18

Document:
{document}

Return only the formatted rules, one per line."""


# =============================================================================
# SHIPPING CARRIER PRICING
# =============================================================================

class ShippingConfig:
    """Shipping carrier pricing formulas"""
    
    class FedEx:
        BASE_RATE = 5.00
        WEIGHT_RATE = 0.50  # per lb
        DISTANCE_RATE = 0.10  # per mile
        
    class UPS:
        BASE_RATE = 4.50
        WEIGHT_RATE = 0.55  # per lb
        DISTANCE_RATE = 0.08  # per mile
        
    class USPS:
        BASE_RATE = 3.50
        WEIGHT_RATE = 0.45  # per lb
        DISTANCE_RATE = 0.05  # per mile
    
    # Priority shipping
    PRIORITY_FEE = 15.00


# =============================================================================
# BUSINESS RULES DEFAULTS
# =============================================================================

class BusinessRulesConfig:
    """Default business rules and settings"""
    
    # Default rules when no document is provided
    DEFAULT_RULES = [
        'age > 18 && location == "NY" -> ApplyDiscount(10)',
        'total >= 500 -> ApplyDiscount(5)'
    ]
    
    # Rule priority settings
    PRIORITY_BASED_ON_COMPLEXITY = True  # More complex conditions = higher priority


# =============================================================================
# UI CONFIGURATION
# =============================================================================

class UIConfig:
    """Gradio UI settings"""
    
    # Server settings
    SERVER_NAME = "127.0.0.1"
    SERVER_PORT = 7860
    SHARE = False  # Set to True to create public link
    
    # UI Appearance
    THEME = "soft"  # Options: "soft", "default", "glass", "monochrome"
    
    # Example data for UI
    MANUAL_ENTRY_PLACEHOLDER = '''age > 18 && location == "NY" -> ApplyDiscount(10)
weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)
total >= 500 -> ApplyDiscount(5)'''
    
    TEST_DATA_PLACEHOLDER = '{"age": 25, "location": "NY", "total": 600, "weight": 4.5, "distance": 80}'


# =============================================================================
# LOGGING AND DEBUG
# =============================================================================

class DebugConfig:
    """Debug and logging settings"""
    
    VERBOSE = True  # Print handler chain progress
    LOG_RULE_EVALUATION = False  # Log each rule evaluation
    SHOW_PARSE_TREE = False  # Show expression tree structure


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_ai_config():
    """Get AI configuration with validation"""
    if AIConfig.USE_LANGCHAIN and not AIConfig.OPENAI_API_KEY:
        print("Warning: Langchain enabled but no API key found.")
        print("Set OPENAI_API_KEY environment variable or configure in config.py")
    
    return {
        "use_langchain": AIConfig.USE_LANGCHAIN,
        "model": AIConfig.MODEL_NAME,
        "temperature": AIConfig.TEMPERATURE,
        "api_key": AIConfig.OPENAI_API_KEY,
        "max_tokens": AIConfig.MAX_TOKENS,
    }


def get_prompt_config():
    """Get prompt configuration"""
    return {
        "system_prompt": PromptTemplates.SYSTEM_PROMPT,
        "extraction_template": PromptTemplates.EXTRACTION_PROMPT_TEMPLATE,
    }


def get_shipping_config():
    """Get shipping configuration"""
    return {
        "fedex": {
            "base": ShippingConfig.FedEx.BASE_RATE,
            "weight_rate": ShippingConfig.FedEx.WEIGHT_RATE,
            "distance_rate": ShippingConfig.FedEx.DISTANCE_RATE,
        },
        "ups": {
            "base": ShippingConfig.UPS.BASE_RATE,
            "weight_rate": ShippingConfig.UPS.WEIGHT_RATE,
            "distance_rate": ShippingConfig.UPS.DISTANCE_RATE,
        },
        "usps": {
            "base": ShippingConfig.USPS.BASE_RATE,
            "weight_rate": ShippingConfig.USPS.WEIGHT_RATE,
            "distance_rate": ShippingConfig.USPS.DISTANCE_RATE,
        },
        "priority_fee": ShippingConfig.PRIORITY_FEE,
    }


# =============================================================================
# QUICK SETUP GUIDE
# =============================================================================

"""
Quick Setup Guide:
==================

1. Enable AI Extraction:
   - Set AIConfig.USE_LANGCHAIN = True
   - Set environment variable: export OPENAI_API_KEY="sk-..."
   - Or directly: AIConfig.OPENAI_API_KEY = "sk-..."

2. Change AI Model:
   - AIConfig.MODEL_NAME = "gpt-4"  # or "gpt-3.5-turbo", "gpt-4-turbo"

3. Adjust Shipping Rates:
   - Edit ShippingConfig.FedEx.BASE_RATE, etc.

4. Customize Prompts:
   - Edit PromptTemplates.SYSTEM_PROMPT
   - Edit PromptTemplates.EXTRACTION_PROMPT_TEMPLATE

5. Change UI Settings:
   - UIConfig.SERVER_PORT = 8080
   - UIConfig.SHARE = True  # for public link

6. Debug Mode:
   - DebugConfig.VERBOSE = True
   - DebugConfig.LOG_RULE_EVALUATION = True
"""
