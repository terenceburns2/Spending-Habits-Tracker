import random, string
from datetime import datetime
from fuzzywuzzy import fuzz
from spendingtracker.main.utils import get_all_transactions



def get_UUID():
    """
    Generate a random transaction UUID
    :return: UUID, e.g. "69082761-2c4e-450b-90bb-5570cd76881e"
    """
    # First part: (8 digits)
    str_list1 = ''.join(random.sample(string.digits*5 + string.ascii_lowercase, 8))
    # Second part: (4 digits)
    str_list2 = ''.join(random.sample(string.digits*3 + string.ascii_lowercase, 4))
    # Third part: (4 digits)
    str_list3 = ''.join(random.sample(string.digits*3 + string.ascii_lowercase, 4))
    # Fourth part: (4 digits)
    str_list4 = ''.join(random.sample(string.digits*3 + string.ascii_lowercase, 4))
    # Fifth part: (12 digits)
    str_list5 = ''.join(random.sample(string.digits*3 + string.ascii_lowercase, 12))
    return str_list1 + '-' + str_list2 + '-' + str_list3 + '-' + str_list4 + '-' + str_list5


def get_amount(min=1, max=200):
    """
    Generate a random amount
    :param min: minimum transaction amount
    :param max: maximum transaction amount
    :return: a random transaction amount, e.g. "13.69"
    """
    return round(random.uniform(min, max), 2)


def get_currency():
    """
    Generate a random currency
    :return: a currency, e.g. "GBP"
    """
    # Please add currency in currencies list
    currencies = ['GBP']
    return currencies[random.randint(0, len(currencies) - 1)]


def get_datetime():
    """
    Generate a timestamp whose class type is 'datetime.datetime'
    Parameter: min_year: the start year; max_year: the end year
    :return: a random date time between 2020-3-8 08:50:24 and current time,
    "yyyy-mm-dd hh:mm:ss" e.g. "2020-02-19 18:00:27"
    """
    # start_datetime = datetime(2020, 3, 8, 8, 50, 24)
    start_datetime = datetime(datetime.utcnow().year, datetime.utcnow().month, 1, 0, 00, 00)
    # end_datetime = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime(datetime.utcnow().year, datetime.utcnow().month + 1, 1, 0, 00, 00)
    delta = end_datetime - start_datetime
    time = start_datetime + delta * random.random()
    return time


def read_matching_table(file='spendingtracker/cards/description.txt'):
    """
    Read the matching table and store them into a tuple
    :param file: relative path to the description.txt file
    :return: a tuple, e.g. "(('Greggs', 'food'), ('Tesco', 'food'))"
    """
    f = open(file, 'r')
    # Create an empty tuple
    data = ()
    try:
        # Read a line every time
        for line in f:
            # Drop the last '\n'
            line = line.strip('\n')
            # Drop space
            line = line.strip()
            # If there is empty line
            if line == '':
                continue
            # Split the line by ';'
            line = line.split(';')
            # Get the item
            item = line[0]
            # Get the category
            category = line[1]
            # Drop preceding space
            category = category.strip()
            # Store (item, category) pair into tuple
            data += ((item, category),)
    finally:
        f.close()
    return data


def get_similarity(str1, str2):
    """
    Compare two strings and get a similarity value
    :param str1: Real transaction description
    :param str2: Category in local files
    :return: Similarity(int), e.g. 96
    """
    # 'token_sort_ratio()' attempts to account for similar strings that are out of order
    # For example:
    # fuzz.token_sort_ratio("Catherine Gitau M.", "Gitau Catherine")
    # output: 94
    return max(fuzz.partial_ratio(str1, str2), fuzz.token_sort_ratio(str1, str2))


def get_desctiption(file='spendingtracker/cards/transactions.txt'):
    """
    Get a random description
    :param file: path to the description file
    :return: a description e.g. 'Subway, Nottingham, England'
    """
    f = open(file, 'r')
    data = []
    try:
        for line in f:                  # Read one line
            line = line.strip('\n')     # Drop the last '\n'
            line = line.strip()         # Drop space
            if line == '':              # If there is empty line
                continue
            data += [line]
    finally:
        f.close()
    return data[random.randint(0, len(data) - 1)]


def classify_transaction(description):
    """
    Automatically classify a transaction
    :param transaction: description of a transaction
    :return: category e.g. 'food'
    """
    table = read_matching_table()
    max_similarity = 0
    index = -1
    for i in range(len(table)):
        similarity = get_similarity(description, table[i][0])
        if similarity > 90:
            if max_similarity < similarity:
                max_similarity = similarity
            index = i
    if index != -1:
        # Return the category with highest similarity
        return table[index][1]
    else:
        # If there is no optimal matching category
        return 'General'


def currency_exchange(currency, amount):
    """
    Do a currency exchange
    :param currency: Transaction currency
    :param amount: Transaction amount
    :return: GBP money
    """
    if currency == 'EUR':
        amount *= 0.88
    elif currency == 'USD':
        amount *= 0.80
    elif currency == 'GBP':
        amount *= 1
    return round(amount, 2)


# Category budget feature:
#   1. Checks if the user has set a budget on a category, if yes then go to step 2
#   2. Checks if the monthly category spending has exceeded the budget, if yes then go to step 3
#   3. Flash a message to the page to tell the user the spending is over the budget
#   4. Checks if the user has opened the budget email service, if yes then go to step 5
#   5. Create the email and send it to the user's email
def category_budget(user, transaction):
    #   0. Checks if the transaction is in this month
    if transaction.timestamp.year != datetime.utcnow().year or transaction.timestamp.month != datetime.utcnow().month:
        return
    #   1. Checks if the user has set a budget on a category, if yes then go to step 2
    spending_over_budget = False
    target_categorybudget = None
    spending = 0
    for categorybudget in user.categorybudgets:
        if transaction.category == categorybudget.category:
            #   2. Checks if the monthly category spending has exceeded the budget, if yes then go to step 3
            spending = get_category_monthly_spending(user, categorybudget.category)
            budget = categorybudget.budget
            print(f"Monthly spending: {spending}")
            print(f"Monthly budget: {budget}")
            if budget - spending < 0:
                spending_over_budget = True
                target_categorybudget = categorybudget
            break
    return (spending_over_budget, target_categorybudget, round(spending, 2))


# Gets the monthly spendings within a specific category for a user
# Inputs: user and category to check
def get_category_monthly_spending(user, category):
    # transactions = get_all_transactions(user, get_current_month_time(), datetime.utcnow())
    transactions = get_all_transactions(user, get_current_month_time(), datetime(datetime.utcnow().year, datetime.utcnow().month + 1, 1, 0, 00, 00))
    category_monthly_spending = 0
    for transaction in transactions:
        if transaction.category == category:
            category_monthly_spending += transaction.amount
    return category_monthly_spending


def get_current_month_time():
    return datetime.strptime(f"{datetime.utcnow().year}-{datetime.utcnow().month}-1 00:00:00", "%Y-%m-%d %H:%M:%S")