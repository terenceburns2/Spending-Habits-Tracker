from spendingtracker import mail
from spendingtracker.common import emails
from spendingtracker.common.utils import flash_message
import traceback
from flask import flash


def send_reset_email(user):
    """
    Send password reset email.
    :param user: user
    :return: None
    """
    msg = emails.reset_email(user)
    try:
        mail.send(msg)
    except Exception as e:
        traceback.print_exc()


def send_budget_email(user):
    """
    Send budget emails.
    To run this method, user' email setting should be on.
    Check if the user spending is over budget; check if the user spending is close to budget (difference <= 50)
    :param user: user
    :return: None
    """
    msg = None
    # total_spending = utils.get_total_spending(utils.get_all_transactions(user))
    print(f"Total spending: {user.spending.totalAccountSpending}; budget: {user.spending.budget}")
    if user.spending.budget - user.spending.totalAccountSpending < 0:
        print(f"Total spending is over budget")
        print("Constructing the email...")
        msg = emails.budget_over_email(user)
        print("Email is constructed!")
    elif user.spending.budget - user.spending.totalAccountSpending <= 50:
        print(f"Total spending is close to budget (difference: {user.spending.budget - user.spending.totalAccountSpending} is <= 50)")
        print("Constructing the 'budget_close_email'...")
        msg = emails.budget_close_email(user)
        print("'budget_close_email' is constructed!")
    else:
        print("User's spending is safe, no email will be sent!")
    if msg != None:
        print("Trying to send 'budget_close_email'...")
        mail.send(msg)
        print("'budget_close_email' is sent successfully!")



# Balance and spending
# Send an email to user if:
#   1. Email setting is on
#   2. Balance is around 0
def send_balance_email(user, card):
    msg = None
    print(f"Recent used card: {card}")
    print(f"Card balance: {card.balance}")
    if card.balance <= 50:
        print("The balance is less than 50.")
        print("Constructing the 'balance_close_email'...")
        msg = emails.balance_close_email(user, card)
        print("'balance_close_email' is constructed!")
    else:
        print("User has sufficient balance, no email will be sent!")
    if msg != None:
        print("Trying to send 'balance_close_email'...")
        mail.send(msg)
        print("'balance_close_email' is sent successfully!")


# printing messages in terminal for debugging purposes
def emails_check(user, card):
    print("************************** emails_check() starts **************************")
    success = True
    balance_status = True
    budget_status = True
    print("Checking if the user has set balance preference...")
    if user.preference.balance:
        print("User balance preference 'ON'")
        try:
            print("Trying to execute 'send_balance_email' function...")
            send_balance_email(user, card)
            print("'send_balance_email' function is executed successfully!")
        except:
            print("'send_balance_email' function is failed!")
            # traceback.print_exc()
            success = False
            balance_status = False
    print("---------------------------------------------------------------------------")
    print("Checking if the user has set budget preference...")
    if user.preference.budget:
        print("User budget preference 'ON'")
        if user.spending.budget != None:
            print("Budget is set")
            try:
                print("Trying to execute 'send_budget_email' function...")
                send_budget_email(user)
                print("'send_budget_email' function is executed successfully!")
            except:
                print("'send_budget_email' function is failed!")
                # traceback.print_exc()
                success = False
                budget_status = False
        else:
            print("Budget is not set")
            print("'send_budget_email' haven't been executed!")
    print("Ending 'emails_check' function...")
    print(f"Balance Status: {'Success' if balance_status else 'Error'}")
    print(f"Budget Status: {'Success' if budget_status else 'Error'}")
    print("************************** emails_check() ends *****************************")
    return success


# printing messages in terminal for debugging purposes
# parsing user and set time interval to see if report can be generated
def send_report_email(user, start_date, end_date):
    msg = None
    if user.preference.report:
        # If the user has no card, he cannot send himself reports
        if not user.cards:
            flash_message("Can't send report, you haven't added card.", 'danger', user.id)
        else:
            # Create a email message
            msg = emails.report_email(user, start_date, end_date)
            print("Trying to send the email...")
            mail.send(msg)
            print("Report email is sent successfully!")
            flash_message("Quarterly Report is sent to your email!", 'success', user.id)
    else:
        flash_message("You haven't activated report email service.", 'info', user.id)


# printing messages in terminal for debugging purposes
def send_category_email(user, categorybudget, spending):
    msg = None
    msg = emails.category_budget_email(user, categorybudget, spending)
    print('Trying to send the email...')
    mail.send(msg)
    print('Category email is sent successfully!')
