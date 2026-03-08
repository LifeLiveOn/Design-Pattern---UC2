from interpreter import AtomicCondition, AndExpression, BusinessRule, BusinessRule, OrExpression, Condition, RuleSet
from context import Context

class ParseTreeGenerator:
    """
    Generates an interpreter expression tree from a rule condition string.

    Example input:
        'age > 18 && location == "New York" || Order.total >= 500'

    Output tree:
        OrExpression(
            AndExpression(AtomicCondition(...), AtomicCondition(...)),
            AndExpression(AtomicCondition(...))
        )
    """

    def __init__(self, expression_txt: str):
        self.expression_txt = expression_txt

    def generate_parse_tree(self):
        """
        Convert the condition string into an interpreter tree.
        """

        # split OR groups first
        or_groups = [group.strip() for group in self.expression_txt.split("||")]

        and_expressions = []

        for group in or_groups:

            # split AND conditions inside each OR group
            and_conditions = [cond.strip() for cond in group.split("&&")]

            atomic_conditions = [
                self._parse_atomic_condition(cond)
                for cond in and_conditions
            ]

            # create AND node
            and_expressions.append(AndExpression(*atomic_conditions))

        # if only one group -> no OR needed
        if len(and_expressions) == 1:
            return and_expressions[0]

        return OrExpression(*and_expressions)

    def _parse_atomic_condition(self, text: str):
        """
        Convert a single condition string into an AtomicCondition object.

        Example:
            'age > 18'
            'location == "NY"'
            'Order.total >= 500'
        """

        operators = [">=", "<=", "==", ">", "<"]

        for op in operators:
            if op in text:
                left, right = text.split(op)

                left = left.strip()
                right = right.strip()

                # remove quotes from strings
                if right.startswith('"') and right.endswith('"'):
                    right = right[1:-1]

                # convert numbers
                else:
                    try:
                        right = float(right)
                        if right.is_integer():
                            right = int(right)
                    except ValueError:
                        pass

                return AtomicCondition(left, op, right)

        raise ValueError(f"Invalid condition: {text}")
    
# example usage
if __name__ == "__main__":
    """
    Example of taking a condition string, generating a parse tree, and evaluating it against a context. This demonstrates how the ParseTreeGenerator can be used to create complex conditions from a simple string representation.
    """
    condition_str = 'age > 18 && location == "New York" || Order.total >= 500'
    generator = ParseTreeGenerator(condition_str)
    parse_tree = generator.generate_parse_tree()
    condition = Condition(parse_tree)

    rule = BusinessRule("rule1", 1, condition, ["Apply 20 % discount"])
    context = Context({
        "age": 25,
        "location": "New York",
        "Order.total": 600
    })
    ruleset = RuleSet("Discount Rules")
    ruleset.add_rule(rule)
    applied_rules = ruleset.evaluate(context)
    print("Applied Rules given Context:",context.data, applied_rules)