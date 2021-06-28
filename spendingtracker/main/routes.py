from flask import Blueprint, render_template, request, abort, redirect, url_for
from flask_login import login_required, current_user
from spendingtracker.models import Transaction, TransactionSchema, Message, MessageSchema, Categorybudget, CategorybudgetSchema
from spendingtracker.common.utils import flash_message
from spendingtracker import db
from spendingtracker.main import utils
from datetime import datetime
from spendingtracker.common.senders import send_report_email
from spendingtracker.cards.utils import read_matching_table


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/homepage', methods=['GET'])
@login_required
def homepage():
    """
    Display the homepage for user.
    :return: 'homepage.html', the dictionary of all transactions, all categories the system knows, current user's category budgets
    """
    # Get all cards of the current user
    cards = current_user.cards
    # Get all transactions of each card and save them in a list
    dict = []
    transaction_schema = TransactionSchema()
    for card in cards:
        # Get all transactions that belong to the current card and order them by descending order
        transactions = Transaction.query.filter_by(card_id=card.id).order_by(Transaction.timestamp.desc())
        for transacion in transactions:
            # Convert SQL object into a list element
            dict_transaction = transaction_schema.dump(transacion)
            dict = dict + [dict_transaction]
    # Get all categories the system knows
    categories = []
    for item in read_matching_table():
        if not item[1] in categories:
            categories += [item[1],]
    #Get current user's category budgets
    categorybudgets = current_user.categorybudgets
    dict2 = []
    categories_schema = CategorybudgetSchema()
    for categorybudget in categorybudgets:
        category = categories_schema.dump(categorybudget)
        dict2 = dict2 + [category]
    return render_template('homepage.html', title='Homepage', transactions=dict, categories=categories, categorybudget=dict2)


# Set user's budget via a request (Ajax).
# This request is sent from budget.js.
# Request method: 'POST' only
# Description:  1. Get the budget (string)
#               2. Alter the current user's budget
#               3. Attach the current time in "%Y-%m-%d %H:%M:%S" format
#               4. Flash a message to user
# Parameter:    1. Float 'budget'
# Return:       1. Result message
@main.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    """
    Set/Change the monthly overall budget.
    This method only accepts 'POST' method.
    If the old budget equals to the new budget, it will do nothing and abort 403 (bad request).
    :return: Abort 403 if the new budget equals the old budget, otherwise returns a success message
    """
    # budget from the request is a string while the budget saved in the db is float
    budget = float(request.form.get('budget'))
    # If the new budget equals to the old budget, abort 403: bad request
    if current_user.spending.budget == budget:
        print("Overall spending budget is already set.")
        abort(403)
    # Otherwise, set the new budget
    current_user.spending.budget = budget
    # Update the budget timestamp
    current_user.spending.budget_set_timestamp = datetime.utcnow()
    db.session.commit()
    flash_message(f'You just set a monthly budget: {budget}!', 'success', current_user.id)
    return f"Budget: ￡{budget} has been set to {current_user.email}"


@main.route('/set_category_budget', methods=['POST'])
@login_required
def set_category_budget():
    """
    This method set/change the category budget.
    This method only accepts 'POST' method.
    This method receives arguments via Ajax.
    If the old budget equals to the new budget, it will do nothing and abort 403 (bad request).
    :return: Abort 403 if the new budget equals the old budget, otherwise returns a success message
    """
    category = request.form.get('category')
    budget = float(request.form.get('budget'))
    # Checks if the budget is already set
    # Go through current user's each category budget and check if the user has already set a budget
    for db_categorybudget in current_user.categorybudgets:
        if category == db_categorybudget.category:
            if budget == db_categorybudget.budget:
                # The user has already set a budget on this category and the new budget equals to the old budget
                print(f"Budget on {category} has already been set.")
                abort(403)
            else:
                # The user has already set a budget on this category but the new budget doesn't equal to the old budget
                # Change the budget
                db_categorybudget.budget = budget
                db.session.commit()
                flash_message(f"Category: {category}, Budget: ￡{budget}", 'success', current_user.id)
                return "Successfully"
    # The user hasn't set a budget on this category
    # Create a new 'Categorybudget' object and save it into the db
    category_budget = Categorybudget(
        category=category,
        budget=budget,
        owner=current_user
    )
    db.session.add(category_budget)
    db.session.commit()
    flash_message(f"Category: {category}, Budget: ￡{budget}", 'success', current_user.id)
    return "Successfully"


@main.route('/remove_budget', methods=['POST'])
@login_required
def remove_budget():
    """
    Remove user's overall spending budget and flash a message.
    If the budget is None, i.e. the user hasn't set a budget, abort 403.
    :return: Abort 403 if the budget is None, otherwise returns a success message
    """
    if current_user.spending.budget == None:
        flash_message(f'You haven\'t set a budget yet.', 'info', current_user.id)
        abort(403)
    else:
        current_user.spending.budget = None
        flash_message(f'You have removed the monthly budget!', 'success', current_user.id)
        return "Successfully removed!"


@main.route('/remove_category_budget', methods=['POST'])
@login_required
def remove_category_budget():
    """
    Remove user's category budget and flash a message.
    If the category budget is None, i.e. the user hasn't set a budget, abort 403
    :return: Abort 403 if the budget is None, otherwise returns a success message
    """
    category = request.form.get('category')
    # Get all category budgets the user has and save them in a list
    user_categories = []
    for db_categorybudget in current_user.categorybudgets:
        user_categories += [db_categorybudget.category,]
    if not category in user_categories:
        flash_message(f'You haven\'t set a budget on {category} yet.', 'info', current_user.id)
        abort(403)
    else:
        print("Deleting...")
        target_categorybudget = Categorybudget.query.filter_by(category=category).first()
        db.session.delete(target_categorybudget)
        db.session.commit()
        print(f"Budget on {category} has been removed.")
        flash_message(f'Budget on {category} has been removed.', 'success', current_user.id)
    return "Success"


@main.route('/help')
def support():
    """
    A tutorial page.
    :return: 'help.html'
    """
    return render_template('help.html', title='Help')


@main.route('/inbox')
@login_required
def inbox():
    """
    A page for users to view their messages.
    :return: 'inbox.html', all flashed messages belong to the current user, list of flashed messages
    """
    messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.desc())
    messages_schema = MessageSchema()
    listOfDict = []
    for message in messages:
        dict_message = messages_schema.dump(message)
        listOfDict += [dict_message]
    return render_template('inbox.html', title='Inbox', messages_flashed=messages, messages_json=listOfDict)


@main.route('/report_mail', methods=['POST'])
@login_required
def report_mail():
    """
    This method handles report requests.
    This method only accepts 'POST' method.
    This method accepts Ajax request.
    It validates the start date and end date of the report, if everything is valid, it will construct a email
    and send it to the user, otherwise prompts error messages.
    :return: 'homepage.html'
    """
    start = request.form.get('start')
    end = request.form.get('end')
    if start == "" or end == "" or start > end:
        flash_message("Invalid dates! Please select valid dates", 'danger', current_user.id)
    else:
        start_date = datetime.strptime(start + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end + " 23:59:59", "%Y-%m-%d %H:%M:%S")
        try:
            send_report_email(current_user, start_date, end_date)
        except:
            print("Failed to send the email!")
            flash_message("An error happened when sending the email. Try Again.", 'danger', current_user.id)
    return redirect(url_for('main.homepage'))






# !!!Ignore this function, it's just for testing!!!
@main.route('/mail_test')
@login_required
def mail_test2():
    user = current_user
    transactions = utils.get_all_transactions(user, user.preference.last_report)
    total_balance = utils.get_all_balance(user)
    total_spending = utils.get_total_spending(transactions)
    weekday_list = utils.get_weekday_spending(transactions)
    categories_list = utils.get_all_categories(transactions)
    html = f"""
    <p class="lead" style="color:black; font-weight: bold;">
        Name: {user.firstname} {user.lastname}
        <br>
        Date: from {user.preference.last_report.strftime("%Y-%m-%d %H:%M")} to {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}
        <br><br>
        Total spent from last report to now: {round(total_spending, 2)}
        <br><br>
        <h3>Average daily expenditure<h3>
        Mondays: {round(weekday_list.get('0', 0), 2)}
        <br>
        Tuesdays: {round(weekday_list.get('1', 0), 2)}
        <br>
        Wednesdays: {round(weekday_list.get('2', 0), 2)}
        <br>
        Thursdays: {round(weekday_list.get('3', 0), 2)}
        <br>
        Fridays: {round(weekday_list.get('4', 0), 2)}
        <br>
        Saturdays: {round(weekday_list.get('5', 0), 2)}
        <br>
        Sundays: {round(weekday_list.get('6', 0), 2)}
        <br><br>

        Overall expenditure:
        <br>
"""
    for key in categories_list:
        html += f"""
            {key}: {round(categories_list[key], 2)}
            <br>
    """
    html += "<p>"
    # user.preference.last_report = datetime.utcnow()
    # db.session.commit()
    return html
