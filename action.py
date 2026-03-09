from abc import ABC, abstractmethod


class ActionCommand(ABC):
    """Abstract Command interface for the Command pattern."""

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)


class Action(ActionCommand):
    """Concrete Command that stores and returns the action text as-is."""

    def __init__(self, action_text: str):
        self.action_text = action_text.strip()

    def execute(self):
        return self.action_text

    def __str__(self):
        return self.action_text


def create_action_command(action_text: str):
    return Action(action_text)

# we can add more complex action types later, e.g. ones that trigger specific functions or side effects
# the main goal is to illustrate the Command pattern and keep the action execution logic separate from the rule evaluation logic in the interpreter


class ApplyDiscount(ActionCommand):
    """Example of a more complex action that could be executed as part of a rule."""

    def __init__(self, discount_percentage: float):
        self.discount_percentage = discount_percentage

    def execute(self):
        # In a real implementation, this would trigger the actual discount logic
        return f"Applying {self.discount_percentage}% discount"

    def __str__(self):
        return f"ApplyDiscount({self.discount_percentage}%)"


# def create_action_command(action_text: str):
#     action_text = action_text.strip()
#     if action_text.startswith("ApplyDiscount(") and action_text.endswith(")"):
#         try:
#             percentage_str = action_text[len("ApplyDiscount("):-1]
#             discount_percentage = float(percentage_str)
#             return ApplyDiscount(discount_percentage)
#         except ValueError:
#             pass  # Fall back to generic Action if parsing fails

#     return Action(action_text)
