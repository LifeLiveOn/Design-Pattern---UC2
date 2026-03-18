from abc import ABC, abstractmethod
import re
from context import Context
from action import Action
from config import BusinessRulesConfig


class Expression(ABC):
    @abstractmethod
    def interpret(self, context) -> bool:
        pass


class AtomicCondition(Expression):

    def __init__(self, left_operand, operator, right_operand):
        self.left_operand = left_operand
        self.operator = operator
        self.right_operand = right_operand

    def interpret(self, context: Context):

        value = context.get_value(self.left_operand)

        if value is None:
            return False

        if self.operator == "==":
            return value == self.right_operand

        if self.operator == ">=":
            return value >= self.right_operand

        if self.operator == ">":
            return value > self.right_operand

        if self.operator == "<=":
            return value <= self.right_operand

        if self.operator == "<":
            return value < self.right_operand

        return False

    def __str__(self):
        right_value = repr(self.right_operand) if isinstance(
            self.right_operand, str) else self.right_operand
        return f"{self.left_operand} {self.operator} {right_value}"

    def __repr__(self):
        return str(self)


class AndExpression(Expression):

    def __init__(self, *expressions: Expression):
        self.expressions = expressions

    def interpret(self, context) -> bool:
        return all(expr.interpret(context) for expr in self.expressions)

    def __str__(self):
        return " && ".join(str(expression) for expression in self.expressions)

    def __repr__(self):
        return str(self)


class OrExpression(Expression):

    def __init__(self, *expressions: Expression):
        self.expressions = expressions

    def interpret(self, context) -> bool:
        return any(expr.interpret(context) for expr in self.expressions)

    def __str__(self):
        return " || ".join(str(expression) for expression in self.expressions)

    def __repr__(self):
        return str(self)


class NotExpression(Expression):

    def __init__(self, expression: Expression):
        self.expression = expression

    def interpret(self, context) -> bool:
        return not self.expression.interpret(context)

    def __str__(self):
        return f"!({self.expression})"

    def __repr__(self):
        return str(self)


class Condition(Expression):
    """
    act as a wrapper around an expression, allowing us to evaluate complex conditions in a more structured way. It can be used to represent a single condition or a combination of conditions using AND, OR, and NOT expressions.
    example: Condition(AndExpression(AtomicCondition("age", ">", 18), AtomicCondition("location", "==", "New York"))) would evaluate to true if the age is greater than 18 and the location is New York.
    """

    def __init__(self, expression: Expression):
        self.expression = expression

    def interpret(self, context) -> bool:
        return self.expression.interpret(context)

    def evaluate(self, context) -> bool:
        return self.expression.interpret(context)

    def __str__(self):
        return str(self.expression)

    def __repr__(self):
        return str(self)


class BusinessRule:

    def __init__(self, rule_id, priority, condition, actions):
        self.rule_id = rule_id
        self.priority = priority
        self.condition = condition
        self.actions = actions
        self.is_active = True

    def evaluate(self, context):

        if not self.is_active:
            return False

        return self.condition.evaluate(context)

    def execute(self, context):
        return [action.execute() for action in self.actions]

    def __str__(self):
        actions_text = ", ".join(str(action) for action in self.actions)
        return f"{self.condition} -> {actions_text}"

    def __repr__(self):
        return str(self)


class RuleSet:
    def __init__(self, name):
        self.name = name
        self.rules: list[BusinessRule] = []

    def add_rule(self, rule: BusinessRule):
        self.rules.append(rule)
        # self.rules.sort(key=lambda r: r.priority, reverse=True)  # Sort by priority (higher first)

    def _sorted_rules(self):
        return sorted(self.rules, key=lambda r: r.priority, reverse=True)

    def _matched_rules(self, context: Context):
        return [rule for rule in self._sorted_rules() if rule.evaluate(context)]

    def _rule_action_text(self, rule: BusinessRule) -> str:
        return ", ".join(str(action) for action in rule.actions)

    def _extract_discount_value(self, action_text: str):
        match = re.fullmatch(
            r"ApplyDiscount\(\s*([0-9]+(?:\.[0-9]+)?)\s*\)", action_text)
        if not match:
            return None
        return float(match.group(1))

    def _select_rules_by_policy(self, matched_rules: list[BusinessRule]):
        policy = getattr(BusinessRulesConfig, "MATCH_POLICY", "all")

        if policy == "highest_priority_only":
            return matched_rules[:1]

        if policy == "max_discount_then_priority":
            discount_candidates = []
            selected_non_discount = []

            for rule in matched_rules:
                action_text = self._rule_action_text(rule)
                discount_value = self._extract_discount_value(action_text)

                if discount_value is None:
                    selected_non_discount.append(rule)
                else:
                    discount_candidates.append((discount_value, rule))

            selected = []

            if discount_candidates:
                max_discount = max(value for value, _ in discount_candidates)
                best_discount_rules = [
                    rule for value, rule in discount_candidates if value == max_discount]
                best_discount_rules = sorted(
                    best_discount_rules, key=lambda r: r.priority, reverse=True)
                selected.append(best_discount_rules[0])

            selected.extend(selected_non_discount)
            return selected

        return matched_rules

    def evaluate(self, context: Context):
        applied_rules = []
        matched_rules = self._matched_rules(context)
        selected_rules = self._select_rules_by_policy(matched_rules)

        for rule in selected_rules:
            action_text = self._rule_action_text(rule)
            applied_rules.append(rule.rule_id + ": " + action_text)
        return applied_rules if applied_rules else "No actions applied"

    def execute(self, context: Context):
        results = []
        matched_rules = self._matched_rules(context)
        selected_rules = self._select_rules_by_policy(matched_rules)
        for rule in selected_rules:
            results.extend(rule.execute(context))
        return results


# example
if __name__ == "__main__":
    c1 = AtomicCondition("age", ">", 18)
    c2 = AtomicCondition("location", "==", "New York")
    c3 = AtomicCondition("total", ">=", 500)
    and_condition = AndExpression(c1, c2, c3)
    condition = Condition(and_condition)

    rule = BusinessRule("rule1", 1, condition, [Action("ApplyDiscount(10)")])
    ruleset = RuleSet("Discount Rules")
    ruleset.add_rule(rule)

    context = Context({
        "age": 25,
        "location": "New York",
        "total": 600
    })
    applied_rules = ruleset.evaluate(context)
    print("Applied Rules given Context:", context.data, applied_rules)
