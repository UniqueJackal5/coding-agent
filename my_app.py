# my_app.py
def calculate_total(price: float, quantity: int) -> float:
    """Calculates the total price given the price per item and the quantity.

    Args:
        price: The price of a single item.
        quantity: The number of items.

    Returns:
        The total price.
    """
    return price * quantity

def greet(name):
    print(f"Hello, {name}!")