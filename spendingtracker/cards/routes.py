from flask import render_template, url_for, redirect, Blueprint, request, abort
from spendingtracker import db
from spendingtracker.cards.forms import AddCardForm
from spendingtracker.models import Card, Transaction, TransactionSchema
from flask_login import current_user, login_required
from spendingtracker.common.utils import flash_message
from spendingtracker.common.senders import emails_check, send_category_email
from spendingtracker.cards.utils import category_budget, read_matching_table
import random


cards = Blueprint('cards', __name__)


@cards.route('/add_card', methods=['GET','POST'])
@login_required
def add_card():
    """
    This methods accepts 'GET' and 'POST' methods. 'POST' method is used for form.
    Only when user sends a form, it's 'POST' methods, otherwise it's 'GET' method.
    Adds a card to current user account.
    User will be asked to input card information and send a form(POST) to '/add_card' url.
    The form is created within this method and bind to the add_card.html file sent to clients.
    If the form is valid, then the new card will be added to the db.
    Then return to homepage, otherwise stay in add_card page/
    :return: URL:'main.homepage' if the form(card) is valid, otherwise 'add_card.html'
    """
    form = AddCardForm()
    # If the client is sending a form, it's a 'POST' request.
    if form.validate_on_submit(): #and form.isCardValid():
        # Randomly generate a balance to that card.
        card = Card(sort_code=form.sort_code.data,
                    card_name=form.card_name.data,
                    account_number=form.account_number.data,
                    owner = current_user,
                    balance=round(random.uniform(100, 3000), 2))
        db.session.add(card)
        db.session.commit()
        # flash messages can be passed between pages, message tag is placed in 'layout.html'
        flash_message(f'Card added for {current_user.email}! You can now track spending', 'success', current_user.id)
        return redirect(url_for('main.homepage'))
    return render_template('add_card.html', title='Add Card', form=form)


@cards.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    """
    This methods accepts 'GET' and 'POST' methods. 'POST' method is used for form.
    Only when user sends a form, it's 'POST' methods, otherwise it's 'GET' method.
    Delete a card from the user account.
    If the form is valid, then the card will be deleted from the db.
    :param card_id: Card id in db.
    :return: URL: 'main.homepage'
    """
    card = Card.query.get_or_404(card_id)
    card_account_number = card.account_number
    # Get all transactions related to this card
    transactions = Transaction.query.filter_by(card_id=card.id)
    # Delete related transactions from the db
    for transaction in transactions:
        db.session.delete(transaction)
    # Delete the card
    db.session.delete(card)
    db.session.commit()
    # Update total spending
    current_user.spending.update_spending()
    db.session.commit()
    # flash messages can be passed between pages, message tag is placed in 'layout.html'
    # flash(f'Card {card_account_number} has been removed!', 'success')
    flash_message(f'Card {card_account_number} has been removed!', 'success', current_user.id)
    return redirect(url_for('main.homepage'))


@cards.route('/card/<int:card_id>')
@login_required
def card(card_id):
    """
    To view a certain card by card id.
    This method will redirect to 'accounts' page
    The card id is passed via request url
    If the user has no card, it will show 404
    :param card_id: Card ID
    :return: 'accounts.html'
    """
    card = Card.query.get_or_404(card_id)
    # Get transactions from db
    # These transactions will be shown in accounts.html, transactions box
    transactions = Transaction.query.filter_by(card_id=card_id).order_by(Transaction.timestamp.desc())
    # Transferring BaseQuery type to Python dictionary data type
    transaction_schema = TransactionSchema()
    # List of all transactions
    listOfDict = []
    # List of all transaction categories
    categories = []
    for transacion in transactions:
        if transacion.category not in categories:
            categories.append(transacion.category)
        dict_transaction = transaction_schema.dump(transacion)
        listOfDict += [dict_transaction]
    # List of all categories known by the system
    all_categories = []
    for item in read_matching_table():
        if not item[1] in all_categories:
            all_categories += [item[1],]
    return render_template('accounts.html', title='Cards', card=card, transactions=listOfDict, categories=categories, all_categories=all_categories, transactions_db=transactions)


@cards.route('/generate_transaction', methods=['POST'])
@login_required
def generate_transaction():
    """
    This method only accepts 'POST' method, and it is used only for Ajax.
    This method accepts a card id and add a new transaction to that card.
    Before generating a new transaction, this method will check if the card
    has sufficient balance. If not, it will flash message to tell the user and abort 403
    After the generation, it will start preference checking, and send corresponding emails.
    :return: Error code 403 if the card has not sufficient balance; 500 if email service is unavailable.
    """
    card_id = request.form.get('card_id')
    card = Card.query.get_or_404(card_id)
    # Generate a random transaction with given card id
    transaction = Transaction(card.id)
    # Update card balance
    if card.check_update_balance(transaction) == False:
        # Not sufficient funds
        flash_message("No sufficient funds", 'danger', current_user.id)
        print('Warning: No sufficient funds')
        return "No sufficient funds"
    # Add the transaction to the db
    db.session.add(transaction)
    db.session.commit()
    # Update total spending
    current_user.spending.update_spending()
    flash_message(f'A new transaction is generated to card:{card.account_number}!', 'success', current_user.id)
    # Check if the latest spending has exceeded user's budget and balance.
    if current_user.spending.check_spending():
        flash_message(f'Your total monthly spending has exceeded your budget!', 'danger', current_user.id)
        print(f'Your spending has exceeded your budget!')
    # Try to send emails to the user if user has email services
    # emails_check() method returns False if the email didn't send out
    if not emails_check(current_user, card):
        flash_message('The email service is currently unavailable!', 'danger', current_user.id)
        print('Error: The email service is currently unavailable!')
    # Checks if the latest spending has exceeded any category budget
    (spending_over_budget, categorybudget, spending) = category_budget(current_user, transaction)
    if spending_over_budget:
        print(spending_over_budget, categorybudget.category, spending)
        flash_message(f'Your monthly budget on {categorybudget.category} has exceeded your budget!', 'danger', current_user.id )
        try:
            send_category_email(current_user, categorybudget, spending)
        except:
            flash_message('The email service is currently unavailable!', 'danger', current_user.id)
            print('Error: The email service is currently unavailable!')
    return "Done"


@cards.route('/change_category', methods=['POST'])
@login_required
def change_category():
    """
    This method receives a Ajax request for updating the category of a transaction.
    This method accepts 'POST' method only.
    This method flashes messages to the page that calls this method to indicate the result of this method.
    :param: 'transactionID': transaction ID (not UUID)
            'newCategory': the new category of the transaction
    :return: 'Succeeded' if the category is changed successfully, 'Failed' otherwise
    """
    transaction_id = request.form.get('transactionID')
    new_category = request.form.get('newCategory')
    # Get the certain transaction object by looking up the transaction ID in 'transaction' table
    transaction = Transaction.query.get_or_404(transaction_id)
    # Temporarily save the old category for flashing messages
    old_category = transaction.category
    try:
        transaction.category = new_category
        flash_message(f'Successfully changed {old_category} to {new_category}', 'success', current_user.id)
        return "Succeeded"
    except:
        flash_message(f'Error: fail to change {old_category} to {new_category}', 'danger', current_user.id)
        return "Failed"









