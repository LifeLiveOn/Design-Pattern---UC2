from abc import ABC, abstractmethod
import ast
import re
from typing import ClassVar
from config import ShippingConfig

class ActionCommand(ABC):
    action_name: ClassVar[str | None] = None
    _registry: ClassVar[dict[str, type["ActionCommand"]]] = {}

    @abstractmethod
    def execute(self, context):
        pass

    @classmethod
    def register(cls, command_cls):
        command_name = command_cls.action_name or command_cls.__name__.removesuffix("Command")
        cls._registry[command_name.lower()] = command_cls
        return command_cls

    @classmethod
    def create_from_text(cls, action_text: str):
        command_name, args = cls._parse_action_text(action_text)

        command_cls = cls._registry.get(command_name.lower())
        if command_cls is None:
            available_commands = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(
                f"Unsupported action '{command_name}'. Registered actions: {available_commands}"
            )

        try:
            return command_cls(*args)
        except TypeError as exc:
            raise ValueError(
                f"Invalid arguments for action '{command_name}': {args}"
            ) from exc

    @classmethod
    def _parse_action_text(cls, action_text: str):
        if not isinstance(action_text, str) or not action_text.strip():
            raise ValueError("Action text must be a non-empty string")

        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$", action_text)
        if not match:
            raise ValueError(f"Invalid action format: {action_text}")

        command_name = match.group(1)
        argument_text = match.group(2).strip()

        if not argument_text:
            return command_name, []

        try:
            call_node = ast.parse(f"f({argument_text})", mode="eval").body
        except SyntaxError as exc:
            raise ValueError(f"Invalid action arguments: {argument_text}") from exc

        if not isinstance(call_node, ast.Call):
            raise ValueError(f"Invalid action arguments: {argument_text}")

        if call_node.keywords:
            raise ValueError("Keyword arguments are not supported in action text")

        try:
            args = [ast.literal_eval(arg) for arg in call_node.args]
        except Exception as exc:
            raise ValueError(
                f"Action arguments must be Python literals: {argument_text}"
            ) from exc

        return command_name, args

    def __str__(self):
        command_name = self.action_name or self.__class__.__name__.removesuffix("Command")
        return f"{command_name}()"

    def __repr__(self):
        return str(self)

@ActionCommand.register
class ApplyDiscountCommand(ActionCommand):
    """
    Example: discount = ApplyDiscountCommand(10)
    discount.execute() -> prints "Applying 10% discount to the order."
    """
    action_name = "ApplyDiscount"

    def __init__(self, discount_percentage):
        self.discount_percentage = discount_percentage

    def execute(self, context):

        total = context.get_value("total")

        new_total = total * (1 - self.discount_percentage / 100)

        context.set_value("total", new_total)

        print(f"Applied {self.discount_percentage}% discount. New total: {new_total}")

        return new_total

    def __str__(self):
        return f"{self.action_name}({self.discount_percentage})"


@ActionCommand.register
class CalculateFedExShippingCommand(ActionCommand):
    """
    Calculate FedEx shipping charge based on weight and distance.
    Example: CalculateFedExShipping(5.5, 100) -> 5.5 lbs, 100 miles
    """
    action_name = "CalculateFedExShipping"

    def __init__(self, weight, distance):
        self.weight = float(weight)
        self.distance = float(distance)

    def execute(self, context):
        # FedEx pricing formula from config
        base_rate = ShippingConfig.FedEx.BASE_RATE
        weight_rate = ShippingConfig.FedEx.WEIGHT_RATE
        distance_rate = ShippingConfig.FedEx.DISTANCE_RATE

        shipping_charge = base_rate + (self.weight * weight_rate) + (self.distance * distance_rate)
        context.set_value("shipping_charge", shipping_charge)
        context.set_value("shipping_carrier", "FedEx")

        print(f"FedEx shipping: {self.weight}lbs, {self.distance}mi = ${shipping_charge:.2f}")
        return shipping_charge

    def __str__(self):
        return f"{self.action_name}({self.weight}, {self.distance})"


@ActionCommand.register
class CalculateUPSShippingCommand(ActionCommand):
    """
    Calculate UPS shipping charge based on weight and distance.
    Example: CalculateUPSShipping(5.5, 100)
    """
    action_name = "CalculateUPSShipping"

    def __init__(self, weight, distance):
        self.weight = float(weight)
        self.distance = float(distance)

    def execute(self, context):
        # UPS pricing formula from config
        base_rate = ShippingConfig.UPS.BASE_RATE
        weight_rate = ShippingConfig.UPS.WEIGHT_RATE
        distance_rate = ShippingConfig.UPS.DISTANCE_RATE

        shipping_charge = base_rate + (self.weight * weight_rate) + (self.distance * distance_rate)
        context.set_value("shipping_charge", shipping_charge)
        context.set_value("shipping_carrier", "UPS")

        print(f"UPS shipping: {self.weight}lbs, {self.distance}mi = ${shipping_charge:.2f}")
        return shipping_charge

    def __str__(self):
        return f"{self.action_name}({self.weight}, {self.distance})"


@ActionCommand.register
class CalculateUSPSShippingCommand(ActionCommand):
    """
    Calculate USPS shipping charge based on weight and distance.
    Example: CalculateUSPSShipping(5.5, 100)
    """
    action_name = "CalculateUSPSShipping"

    def __init__(self, weight, distance):
        self.weight = float(weight)
        self.distance = float(distance)

    def execute(self, context):
        # USPS pricing formula from config
        base_rate = ShippingConfig.USPS.BASE_RATE
        weight_rate = ShippingConfig.USPS.WEIGHT_RATE
        distance_rate = ShippingConfig.USPS.DISTANCE_RATE

        shipping_charge = base_rate + (self.weight * weight_rate) + (self.distance * distance_rate)
        context.set_value("shipping_charge", shipping_charge)
        context.set_value("shipping_carrier", "USPS")

        print(f"USPS shipping: {self.weight}lbs, {self.distance}mi = ${shipping_charge:.2f}")
        return shipping_charge

    def __str__(self):
        return f"{self.action_name}({self.weight}, {self.distance})"


@ActionCommand.register
class SetPriorityShippingCommand(ActionCommand):
    """
    Mark order for priority/express shipping.
    Example: SetPriorityShipping()
    """
    action_name = "SetPriorityShipping"

    def __init__(self):
        pass

    def execute(self, context):
        context.set_value("priority_shipping", True)
        current_charge = context.get_value("shipping_charge") or 0
        priority_fee = ShippingConfig.PRIORITY_FEE
        new_charge = current_charge + priority_fee
        context.set_value("shipping_charge", new_charge)

        print(f"Priority shipping enabled. Additional fee: ${priority_fee:.2f}")
        return new_charge

    def __str__(self):
        return f"{self.action_name}()"


def create_action_command(action_text: str):
    return ActionCommand.create_from_text(action_text)

