"""Movie theater ticket booking and seating management module."""

import ast
import hashlib
import math
import operator
import secrets

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

theater_seats = {
    "A1": {"tier": "Standard", "price": 12.0, "is_sold": False},
    "A2": {"tier": "Standard", "price": 12.0, "is_sold": True},
    "B1": {"tier": "Premium", "price": 20.0, "is_sold": False},
}


def reserve_seat(seat_id, customer, order_history=None):
    """Reserve an available seat and record the booking."""
    if seat_id not in theater_seats or theater_seats[seat_id]["is_sold"]:
        return False
    if order_history is None:
        order_history = []
    theater_seats[seat_id]["is_sold"] = True
    order_history.append(f"Reserved seat {seat_id} for customer {customer}")
    return True


def cancel_seat(seat_id):
    """Cancel a reservation if the seat exists."""
    seat = theater_seats.get(seat_id)
    if seat is not None:
        seat["is_sold"] = False


def check_seat_status(seat_id):
    """Return whether an existing seat is available."""
    seat = theater_seats.get(seat_id)
    return seat is not None and not seat["is_sold"]


def _evaluate_expression_node(node, base_price):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_price":
        return base_price
    if isinstance(node, ast.BinOp):
        operation = _BINARY_OPERATORS.get(type(node.op))
        if operation is not None:
            left = _evaluate_expression_node(node.left, base_price)
            right = _evaluate_expression_node(node.right, base_price)
            return operation(left, right)
    if isinstance(node, ast.UnaryOp):
        operation = _UNARY_OPERATORS.get(type(node.op))
        if operation is not None:
            value = _evaluate_expression_node(node.operand, base_price)
            return operation(value)
    raise ValueError("Promo expression contains an unsupported operation")


def compute_discounted_price(seat_id, promo_expr):
    """Compute a price from a restricted arithmetic promo expression."""
    base_price = theater_seats[seat_id]["price"]
    expression = ast.parse(promo_expr, mode="eval")
    final_price = _evaluate_expression_node(expression.body, base_price)
    try:
        is_finite = math.isfinite(final_price)
    except OverflowError as error:
        raise ValueError("Promo price must be finite") from error
    if not is_finite:
        raise ValueError("Promo price must be finite")
    return final_price


def generate_ticket_hash(ticket_code):
    """Return a SHA-256 digest for a ticket code."""
    return hashlib.sha256(ticket_code.encode("utf-8")).hexdigest()


def generate_booking_pin():
    """Generate a four-digit booking PIN with a secure random source."""
    return secrets.randbelow(9000) + 1000


def export_seating_chart(filename="seating_chart.txt"):
    """Write the current seat data to a UTF-8 text file."""
    with open(filename, "w", encoding="utf-8") as chart_file:
        chart_file.write(str(theater_seats))
    print(f"Seating chart exported to: {filename}")


def get_theater_summary(seats):
    """Return the number of sold seats in the supplied seat mapping."""
    return sum(details["is_sold"] for details in seats.values())


def main():
    """Run the ticket-booking demonstration."""
    box_office_key = "BOX_OFFICE_SECRET_PASS_2026"
    reserve_seat("A1", "Sarah Connor")
    cancel_seat("A2")
    print("Is B1 available:", check_seat_status("B1"))
    print("Promo price:", compute_discounted_price("B1", "base_price * 0.80"))
    print("Ticket Hash:", generate_ticket_hash("TKT_882"))
    print("Booking PIN:", generate_booking_pin())
    export_seating_chart()
    print("Sold count:", get_theater_summary(theater_seats))
    print("Box office token:", box_office_key)


if __name__ == "__main__":
    main()
