from interpreter import AtomicCondition, AndExpression, BusinessRule, BusinessRule, OrExpression, Condition, RuleSet
from context import Context
import uuid
from typing import Optional, List, Any


class RuleNode:
    """
    Represents a single node in the parse tree.

    Attributes:
        nodeId: Unique identifier for this node
        nodeType: Type of node (ATOMIC, AND, OR, NOT)
        value: The condition value (for ATOMIC nodes) or operator
        children: Child nodes in the tree
    """

    def __init__(self, node_type: str, value: Any = None, node_id: str = None):
        self.nodeId = node_id or str(uuid.uuid4())
        self.nodeType = node_type  # ATOMIC, AND, OR, NOT
        self.value = value
        self.children: List['RuleNode'] = []

    def add_child(self, child: 'RuleNode'):
        """Add a child node"""
        self.children.append(child)

    def to_expression(self):
        """Convert RuleNode tree back to Expression objects"""
        if self.nodeType == "ATOMIC":
            left, op, right = self.value
            return AtomicCondition(left, op, right)

        elif self.nodeType == "AND":
            child_expressions = [child.to_expression()
                                 for child in self.children]
            return AndExpression(*child_expressions)

        elif self.nodeType == "OR":
            child_expressions = [child.to_expression()
                                 for child in self.children]
            return OrExpression(*child_expressions)

        elif self.nodeType == "NOT":
            return self.children[0].to_expression()

        raise ValueError(f"Unknown node type: {self.nodeType}")

    def __repr__(self):
        return f"RuleNode(id={self.nodeId}, type={self.nodeType}, value={self.value}, children={len(self.children)})"

    def __str__(self):
        if self.nodeType == "ATOMIC":
            left, op, right = self.value
            return f"{left} {op} {right}"
        elif self.nodeType == "AND":
            return " && ".join(str(child) for child in self.children)
        elif self.nodeType == "OR":
            return " || ".join(str(child) for child in self.children)
        elif self.nodeType == "NOT":
            return f"!({self.children[0]})"
        return str(self.value)

    def label(self) -> str:
        if self.nodeType == "ATOMIC":
            left, op, right = self.value
            return f"ATOMIC: {left} {op} {right}"
        return self.nodeType


class ParseTree:
    """
    Represents a complete parse tree with metadata.

    Attributes:
        treeId: Unique identifier for this tree
        expressionText: Original condition text that generated this tree
        rootNode: Root RuleNode of the tree
    """

    def __init__(self, tree_id: str, expression_text: str, root_node: RuleNode):
        self.treeId = tree_id
        self.expressionText = expression_text
        self.rootNode = root_node

    def get_root_expression(self):
        """Convert the tree back to an Expression for evaluation"""
        return self.rootNode.to_expression()

    def evaluate(self, context: Context) -> bool:
        """Evaluate the tree against a context"""
        expression = self.get_root_expression()
        return expression.interpret(context)

    def interpret(self, context: Context) -> bool:
        """Compatibility method so ParseTree can be used where Expression is expected."""
        return self.evaluate(context)

    def to_ascii(self) -> str:
        """Return a readable ASCII tree visualization."""
        lines = [f"ParseTree<{self.treeId}>: {self.expressionText}"]
        lines.extend(self._ascii_lines(self.rootNode, prefix="", is_last=True))
        return "\n".join(lines)

    def to_mermaid(self) -> str:
        """
        Return Mermaid graph text for visualization tools.
        Example usage with markdown:
            ```mermaid
            {parse_tree.to_mermaid()}
            ```
        """
        lines = ["graph TD"]
        node_ids: dict[int, str] = {}

        def walk(node: RuleNode):
            key = id(node)
            if key not in node_ids:
                node_ids[key] = f"N{len(node_ids) + 1}"

            current_id = node_ids[key]
            current_label = self._escape_mermaid_label(node.label())
            lines.append(f"    {current_id}[\"{current_label}\"]")

            for child in node.children:
                child_key = id(child)
                if child_key not in node_ids:
                    node_ids[child_key] = f"N{len(node_ids) + 1}"

                child_id = node_ids[child_key]
                lines.append(f"    {current_id} --> {child_id}")
                walk(child)

        walk(self.rootNode)
        return "\n".join(lines)

    def _ascii_lines(self, node: RuleNode, prefix: str, is_last: bool) -> list[str]:
        connector = "└── " if is_last else "├── "
        lines = [f"{prefix}{connector}{node.label()} [{node.nodeId[:8]}]"]

        next_prefix = f"{prefix}{'    ' if is_last else '│   '}"
        for index, child in enumerate(node.children):
            child_is_last = index == len(node.children) - 1
            lines.extend(self._ascii_lines(child, next_prefix, child_is_last))

        return lines

    def _escape_mermaid_label(self, label: str) -> str:
        return str(label).replace('"', "\\\"")

    def __str__(self):
        return f"ParseTree({self.treeId}): {self.expressionText}"

    def __repr__(self):
        return f"ParseTree(id={self.treeId}, expr={self.expressionText}, root={self.rootNode})"


class ParseTreeGenerator:
    """
    Generates a ParseTree (with RuleNode structure) from a rule condition string.

    Example input:
        'age > 18 && location == "New York" || Order.total >= 500'

    Output ParseTree:
        ParseTree with rootNode containing:
            OrExpression(
                AndExpression(AtomicCondition(...), AtomicCondition(...)),
                AndExpression(AtomicCondition(...))
            )
    """

    def __init__(self, expression_txt: str, tree_id: str = None):
        self.expression_txt = expression_txt
        self.tree_id = tree_id or str(uuid.uuid4())

    def generate_parse_tree(self) -> ParseTree:
        """
        Convert the condition string into a ParseTree with RuleNode structure.
        Returns a ParseTree object containing the root RuleNode.
        """

        # split OR groups first
        or_groups = [group.strip()
                     for group in self.expression_txt.split("||")]

        and_nodes = []

        for group in or_groups:
            # split AND conditions inside each OR group
            and_conditions = [cond.strip() for cond in group.split("&&")]

            atomic_nodes = [
                self._parse_atomic_condition(cond)
                for cond in and_conditions
            ]

            # create AND node
            and_node = RuleNode("AND")
            for atomic_node in atomic_nodes:
                and_node.add_child(atomic_node)

            and_nodes.append(and_node)

        # if only one group -> no OR needed (root is the AND node)
        if len(and_nodes) == 1:
            root_node = and_nodes[0]
        else:
            # create OR root node
            root_node = RuleNode("OR")
            for and_node in and_nodes:
                root_node.add_child(and_node)

        # Create and return ParseTree
        return ParseTree(self.tree_id, self.expression_txt, root_node)

    def _parse_atomic_condition(self, text: str) -> RuleNode:
        """
        Convert a single condition string into a RuleNode (ATOMIC type).

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

                # Create ATOMIC node with value=(left, operator, right)
                return RuleNode("ATOMIC", value=(left, op, right))

        # No operator found — treat as a boolean flag (e.g. "international orders")
        return RuleNode("ATOMIC", value=(text.strip(), "==", True))


# example usage
if __name__ == "__main__":
    """
    Example of taking a condition string, generating a parse tree, and evaluating it against a context.
    This demonstrates how the ParseTreeGenerator can be used to create complex conditions from a simple string representation.
    """
    condition_str = 'age > 18 && location == "New York" || Order.total >= 500'
    generator = ParseTreeGenerator(condition_str)
    parse_tree = generator.generate_parse_tree()

    print(f"Generated Parse Tree: {parse_tree}")
    print(f"Tree ID: {parse_tree.treeId}")
    print(f"Expression Text: {parse_tree.expressionText}")
    print(f"Root Node: {parse_tree.rootNode}")

    # Convert back to expression for evaluation
    expression = parse_tree.get_root_expression()
    condition = Condition(expression)

    rule = BusinessRule("rule1", 1, condition, ["Apply 20 % discount"])
    context = Context({
        "age": 25,
        "location": "New York",
        "Order.total": 600
    })
    ruleset = RuleSet("Discount Rules")
    ruleset.add_rule(rule)
    applied_rules = ruleset.evaluate(context)
    print("Applied Rules given Context:", context.data, applied_rules)
