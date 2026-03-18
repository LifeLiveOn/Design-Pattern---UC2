# Implement chain of responsibility
import re
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
    PRIORITY_PATTERN = re.compile(
        r"^\[?P\s*=\s*(\d{1,3})\]?\s*(.*)$", re.IGNORECASE)

    def process(self, rules):
        if DebugConfig.VERBOSE:
            print("Ranking rules")

        # If AI assigned explicit priorities like [P=90], honor them first
        if any(self._extract_explicit_priority(rule)[0] is not None for rule in rules):
            return sorted(rules, key=self._ranking_key, reverse=True)

        if BusinessRulesConfig.PRIORITY_BASED_ON_COMPLEXITY:
            return sorted(rules, key=lambda r: r.count("&&"), reverse=True)

        return rules

    def _extract_explicit_priority(self, rule_text):
        match = self.PRIORITY_PATTERN.match(rule_text.strip())
        if not match:
            return None, rule_text
        return int(match.group(1)), match.group(2).strip()

    def _ranking_key(self, rule_text):
        explicit_priority, cleaned_rule = self._extract_explicit_priority(
            rule_text)
        complexity = cleaned_rule.count("&&")

        if explicit_priority is None:
            return (0, complexity)

        return (1, explicit_priority)


class ParseTreeGenerationHandler(Handler):
    """
    RULE example: 'age > 18 && location == "NY" -> ApplyDiscount(10)'
    This handler will convert the condition part of the rule into a parse tree that can be evaluated by the interpreter.
    """
    PRIORITY_PATTERN = re.compile(
        r"^\[?P\s*=\s*(\d{1,3})\]?\s*(.*)$", re.IGNORECASE)

    def process(self, rules):

        parsed_rules = []
        total_rules = len(rules)

        for index, rule in enumerate(rules, start=1):

            explicit_priority, cleaned_rule_text = self._extract_explicit_priority(
                rule)

            condition_text, action_text = self._split_rule(cleaned_rule_text)

            parser = ParseTreeGenerator(condition_text)

            parse_tree = parser.generate_parse_tree()

            expression = parse_tree.get_root_expression()

            condition = Condition(expression)

            command = create_action_command(action_text)

            priority = explicit_priority if explicit_priority is not None else (
                total_rules - index + 1)

            business_rule = BusinessRule(
                f"rule_{index}", priority, condition, [command])

            business_rule.parse_tree = parse_tree

            parsed_rules.append(business_rule)

        return parsed_rules

    def _split_rule(self, rule_text):
        if "->" not in rule_text:
            raise ValueError(
                f"Rule is missing action separator '->': {rule_text}")

        condition_text, action_text = rule_text.split("->", 1)
        return condition_text.strip(), action_text.strip()

    def _extract_explicit_priority(self, rule_text):
        match = self.PRIORITY_PATTERN.match(rule_text.strip())
        if not match:
            return None, rule_text

        priority = max(0, min(100, int(match.group(1))))
        cleaned_rule = match.group(2).strip()
        return priority, cleaned_rule


pipeline = RuleExtraction(RuleNormalization(
    RuleRanking(ParseTreeGenerationHandler())))

if __name__ == "__main__":
    rules = pipeline.handle(
        "age > 18 && location == \"NY\" -> ApplyDiscount(10)\ntotal >= 10000 -> ApplyDiscount(5)")
    print(f"Generated {len(rules)} rules", [str(rule) for rule in rules])
