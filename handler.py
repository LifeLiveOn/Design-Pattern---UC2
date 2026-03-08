# Implement chain of responsibility 
from parseTree import ParseTreeGenerator
from interpreter import Condition, BusinessRule
from action import create_action_command
from config import BusinessRulesConfig, DebugConfig


class Handler:
    def __init__(self, next_handler=None):
        self.next = next_handler
    
    def handle(self, request):
        processed = self.process(request)
        if self.next:
            return self.next.handle(processed)
        return processed
    
    def process(self, request):
        raise NotImplementedError("Must implement process method in subclass")

class RuleExtraction(Handler):
    DEFAULT_RULES = BusinessRulesConfig.DEFAULT_RULES

    def process(self, document):

        if DebugConfig.VERBOSE:
            print("Extracting rules")

        if isinstance(document, list):
            return document

        if isinstance(document, str):
            extracted_rules = [
                line.strip()
                for line in document.splitlines()
                if line.strip() and "->" in line
            ]
            if extracted_rules:
                return extracted_rules

        return self.DEFAULT_RULES.copy()

class RuleNormalization(Handler):
    def process(self, rules):
        if DebugConfig.VERBOSE:
            print("Normalizing rules")
        return [" ".join(rule.strip().split()) for rule in rules]

class RuleRanking(Handler):
    def process(self, rules):
        if DebugConfig.VERBOSE:
            print("Ranking rules")
        # This is a placeholder for actual ranking logic
        if BusinessRulesConfig.PRIORITY_BASED_ON_COMPLEXITY:
            return sorted(rules, key=lambda r: r.count("&&"), reverse=True)
        return rules

class ParseTreeGenerationHandler(Handler):
    """
    RULE example: 'age > 18 && location == "NY" -> ApplyDiscount(10)'
    This handler will convert the condition part of the rule into a parse tree that can be evaluated by the interpreter.
    """

    def process(self, rules):

        parsed_rules = []
        total_rules = len(rules)

        for index, rule in enumerate(rules, start=1):

            condition_text, action_text = self._split_rule(rule)

            parser = ParseTreeGenerator(condition_text)

            expression = parser.generate_parse_tree()

            condition = Condition(expression)

            command = create_action_command(action_text)

            priority = total_rules - index + 1

            parsed_rules.append(
                BusinessRule(f"rule_{index}", priority, condition, [command])
            )

        return parsed_rules

    def _split_rule(self, rule_text):
        if "->" not in rule_text:
            raise ValueError(f"Rule is missing action separator '->': {rule_text}")

        condition_text, action_text = rule_text.split("->", 1)
        return condition_text.strip(), action_text.strip()

pipeline = RuleExtraction(RuleNormalization(RuleRanking(ParseTreeGenerationHandler())))

if __name__ == "__main__":
    rules = pipeline.handle("age > 18 && location == \"NY\" -> ApplyDiscount(10)\ntotal >= 10000 -> ApplyDiscount(5)")
    print(f"Generated {len(rules)} rules", [str(rule) for rule in rules])

