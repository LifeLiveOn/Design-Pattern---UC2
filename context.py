import json


class Context:
    """
    A class to hold the context data for our rules engines
    """

    def __init__(self, data: dict):
        self.data = json.loads(data) if isinstance(data, str) else data

    def get_value(self, key: str):
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        return self.data.get(key, None)

    def set_value(self, key: str, value):
        if not isinstance(key, str):
            raise ValueError("Key must be a string.")
        self.data[key] = value


# Example usage:
if __name__ == "__main__":
    context_data = {
        "user": "Alice",
        "age": 30,
        "location": "New York"
    }

    context = Context(context_data)

    print(context.get_value("user"))  # Output: Alice
    print(context.get_value("age"))   # Output: 30
    print(context.get_value("location"))  # Output: New York
    print(context.get_value("nonexistent_key"))  # Output: None
    context.set_value("total", 100)
    print(context.get_value("total"))  # Output: 100
