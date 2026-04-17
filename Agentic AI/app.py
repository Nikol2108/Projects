def calculate_total_price(prices):
    total = 0

    for price in prices:
        total += price

    return total


def main():
    orders = [10.5, 20.0, "oops", 5.0]
    print(f"Total price: {calculate_total_price(orders)}")


if __name__ == "__main__":
    main()
