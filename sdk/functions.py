def validate_credit_card(card_number: str) -> bool:
    """This function validates a credit card number."""
    card_number = [int(num) for num in card_number]
    checkDigit = card_number.pop(-1)
    card_number.reverse()
    card_number = [num * 2 if idx % 2 == 0
                   else num for idx, num in enumerate(card_number)]
    card_number = [num - 9 if idx % 2 == 0 and num > 9
                   else num for idx, num in enumerate(card_number)]
    card_number.append(checkDigit)
    checkSum = sum(card_number)
    return checkSum % 10 == 0