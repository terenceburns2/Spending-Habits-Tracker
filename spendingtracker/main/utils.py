


# Get a list of all transactions belong to the user
def get_all_transactions(user, start_date, end_date):
    transactions = []
    for card in user.cards:
        for transaction in card.transactions:
            transaction_datetime = transaction.timestamp
            if transaction_datetime >= start_date and transaction_datetime <= end_date:
                transactions.append(transaction)
    return transactions


# Get balance of all cards belong to the user
def get_all_balance(user):
    total_balance = 0
    for card in user.cards:
        total_balance += card.balance
    return total_balance


# Get total spending of all transactions
def get_total_spending(transactions):
    total_spending = 0
    for transaction in transactions:
        total_spending += transaction.amount
    return round(total_spending, 2)


# Get a dictionary of transaction categories and corresponding amount
# Transactions should be later than the last_datetime
def get_all_categories(transactions):
    categories_list = {}
    for transaction in transactions:
        category = str(transaction.category)
        if category in categories_list:
            categories_list[category] += transaction.amount
        else:
            categories_list[category] = transaction.amount
    return categories_list


# Get a dictionary of transaction happened on each weekday and corresponding average amount
# Transactions should be later than the last_datetime
def get_weekday_spending(transactions):
    weekday_list = {}
    for transaction in transactions:
        transaction_datetime = transaction.timestamp
        # Converts 'int' to 'str': 0 -> '0' (Monday); 1 -> '1' (Tuesday); ...
        week_day = str(transaction_datetime.weekday())
        # If the week day is already created or assigned with values
        if week_day in weekday_list:
            weekday_list[week_day]['amount'] += transaction.amount
            weekday_list[week_day]['days'] += 1
        else:
            weekday_list[week_day] = {}
            weekday_list[week_day]['amount'] = transaction.amount
            weekday_list[week_day]['days'] = 1
    res_list = {}
    for key in weekday_list:
        res_list[key] = round(weekday_list[key]['amount'] / weekday_list[key]['days'], 2)
    return res_list


