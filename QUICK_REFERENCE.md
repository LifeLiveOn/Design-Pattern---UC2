# Quick Reference - Business Rules Format

## Rule Syntax
```
condition -> action
```

## Conditions

### Operators
- `==` Equal to
- `!=` Not equal to
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal
- `<=` Less than or equal

### Logical Operators
- `&&` AND (both conditions must be true)
- `||` OR (at least one condition must be true)

### Examples
```
age > 18
location == "NY"
weight <= 5
age > 18 && location == "NY"
weight > 10 || distance > 200
```

## Actions

### Discount Actions
```
ApplyDiscount(percentage)
```
**Examples:**
- `age > 65 -> ApplyDiscount(15)` *(15% senior discount)*
- `total >= 500 -> ApplyDiscount(5)` *(5% bulk discount)*

### Shipping Actions

#### FedEx
```
CalculateFedExShipping(weight, distance)
```
**Example:**
- `weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)`

#### UPS
```
CalculateUPSShipping(weight, distance)
```
**Example:**
- `weight > 10 -> CalculateUPSShipping(12, 250)`

#### USPS
```
CalculateUSPSShipping(weight, distance)
```
**Example:**
- `weight <= 2 -> CalculateUSPSShipping(1.5, 50)`

#### Priority Shipping
```
SetPriorityShipping()
```
**Example:**
- `order_value > 500 -> SetPriorityShipping()`

## Complete Examples

### Discount Rules
```
age > 65 -> ApplyDiscount(15)
age > 18 && location == "NY" -> ApplyDiscount(10)
total >= 500 -> ApplyDiscount(5)
```

### Shipping Rules
```
weight <= 5 && distance <= 100 -> CalculateFedExShipping(4.5, 80)
weight > 10 && distance > 200 -> CalculateUPSShipping(12, 250)
weight <= 2 && distance <= 50 -> CalculateUSPSShipping(1.5, 40)
order_value > 500 -> SetPriorityShipping()
```

### Mixed Rules
```
age > 65 -> ApplyDiscount(15)
weight <= 5 -> CalculateFedExShipping(4.5, 80)
total >= 500 -> ApplyDiscount(5)
order_value > 500 -> SetPriorityShipping()
```

## Test Data Format (JSON)

### Discount Test
```json
{
  "age": 70,
  "location": "NY",
  "total": 600
}
```

### Shipping Test
```json
{
  "weight": 4.5,
  "distance": 80,
  "order_value": 550
}
```

### Combined Test
```json
{
  "age": 70,
  "location": "NY",
  "total": 600,
  "weight": 3,
  "distance": 50,
  "order_value": 650
}
```

## Common Variables

### Customer Attributes
- `age` - Customer age (number)
- `location` - Customer location (string, use quotes)
- `occupation` - Customer occupation (string)

### Order Attributes
- `total` - Order total amount ($)
- `order_value` - Total order value ($)
- `quantity` - Number of items

### Shipping Attributes
- `weight` - Package weight (lbs)
- `distance` - Shipping distance (miles)
- `priority` - Priority flag (string)

## Tips

1. **Strings must be quoted**: `location == "NY"` ✅ not `location == NY` ❌
2. **Numbers are not quoted**: `age > 18` ✅ not `age > "18"` ❌
3. **Multiple conditions**: Use `&&` for AND, `||` for OR
4. **One rule per line**: Each rule should be on its own line
5. **Test with realistic data**: Use JSON objects that match your conditions
