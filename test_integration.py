"""
Quick test to verify all components work together before launching UI
"""

from interpreter import RuleSet
from template import BusinessRuleController
from context import Context


def test_manual_flow():
    """Test manual rule addition with discounts"""
    print("=" * 60)
    print("Testing Manual Rule Flow - Discount Rules")
    print("=" * 60)
    
    ruleset = RuleSet("Test Rules")
    controller = BusinessRuleController(ruleset)
    
    # Add manual rules
    rules_text = '''age > 18 && location == "NY" -> ApplyDiscount(10)
total >= 500 -> ApplyDiscount(5)
age > 65 -> ApplyDiscount(15)'''
    
    controller.update_rules_manual(rules_text)
    
    # List rules
    print("\nLoaded Rules:")
    for rule in controller.list_rules():
        print(f"  {rule}")
    
    # Test with data
    test_data = {"age": 70, "location": "NY", "total": 600}
    print(f"\nTest Data: {test_data}")
    
    result = controller.process_request(test_data)
    print(f"Applied Rules: {result}")
    
    print("\n✅ Manual flow test passed!\n")


def test_ai_flow():
    """Test AI rule extraction flow with shipping rules"""
    print("=" * 60)
    print("Testing AI Rule Extraction Flow - Shipping Rules")
    print("=" * 60)
    
    ruleset = RuleSet("AI Test Rules")
    controller = BusinessRuleController(ruleset)
    
    # Simulate document with mixed rules (discount + shipping)
    document = '''age > 18 && location == "NY" -> ApplyDiscount(10)
total >= 500 -> ApplyDiscount(5)
weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)
weight > 10 -> CalculateUPSShipping(12, 250)
order_value > 500 -> SetPriorityShipping()'''
    
    controller.update_rules_ai(document)
    
    # List rules
    print("\nExtracted Rules:")
    for rule in controller.list_rules():
        print(f"  {rule}")
    
    # Test with shipping data
    test_data = {"age": 25, "location": "NY", "weight": 4.5, "distance": 80, "order_value": 600, "total": 100}
    print(f"\nTest Data: {test_data}")
    
    result = controller.process_request(test_data)
    print(f"Applied Rules: {result}")
    
    print("\n✅ AI flow test passed!\n")


def test_action_flexibility():
    """Test that action system supports multiple business scenarios"""
    print("=" * 60)
    print("Testing Action System Flexibility")
    print("=" * 60)
    
    from action import create_action_command, ActionCommand
    
    # Test creating discount commands
    cmd1 = create_action_command("ApplyDiscount(10)")
    print(f"Discount command: {cmd1}")
    
    # Test creating shipping commands
    cmd2 = create_action_command("CalculateFedExShipping(5.5, 100)")
    print(f"FedEx command: {cmd2}")
    
    cmd3 = create_action_command("CalculateUPSShipping(12, 250)")
    print(f"UPS command: {cmd3}")
    
    cmd4 = create_action_command("CalculateUSPSShipping(2, 50)")
    print(f"USPS command: {cmd4}")
    
    cmd5 = create_action_command("SetPriorityShipping()")
    print(f"Priority command: {cmd5}")
    
    # Show all registered commands
    print(f"\nRegistered action commands: {sorted(ActionCommand._registry.keys())}")
    print(f"Total commands available: {len(ActionCommand._registry)}")
    
    print("\n✅ Action system test passed!\n")


if __name__ == "__main__":
    try:
        test_manual_flow()
        test_ai_flow()
        test_action_flexibility()
        
        print("=" * 60)
        print("🎉 All integration tests passed!")
        print("=" * 60)
        print("\nYou can now run the UI with: python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
