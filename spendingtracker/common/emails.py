from flask import url_for
from flask_mail import Message
from spendingtracker.main import utils
from datetime import datetime


def reset_email(user):
    """
    Create a email message for the user.
    The email contains the reset token and the url for changing password.
    :param user: user
    :return: email message
    """
    # create a token
    token = user.get_reset_token()
    # create the email message
    msg = Message('Password Reset Request', sender='noreply@gmail.com', recipients=[user.email])
    # _external=True here can give an absolute url rather than a relative url, which is normally returned by url_for()
    msg.html = f"""
        <header
            style="background-color:#033877; display:flex;">
            <img src="https://thebankly.com/wp-content/uploads/2019/01/getmyoffercapitalone.jpg" 
                class="img-fluid"
                alt="Capital One homepage"
                style="float:center; width:150px; height:45px; padding:30px;">
            <h1 style="text-align:center; color:white; padding:15px;">Capital One</h1>
        </header>
        <p class="lead" style="text-color:black;">
            To reset your password, visit the following link:
            {url_for('users.reset_token', token=token, _external=True)}<p>

        If you did not make this request then simply ignore this email and no change will be made.

    """
    return msg


def budget_over_email(user):
    """
    Create a email message for the user.
    The email contains user's spending and his budget and tells the user that
    the spending has exceeded the budget.
    :param user: user
    :return: email message
    """
    # create the email message
    msg = Message('Your Spending is Over Budget', sender='noreply@gmail.com', recipients=[user.email])
    # '_external=True' here gives an absolute url rather than a relative url
    msg.html = f"""
        <header
            style="background-color:#033877; display:flex;">
            <img src="https://thebankly.com/wp-content/uploads/2019/01/getmyoffercapitalone.jpg" 
                class="img-fluid"
                alt="Capital One homepage"
                style="float:center; width:150px; height:45px; padding:30px;">
            <h1 style="text-align:center; color:white; padding:15px;">Capital One</h1>
        </header>
        <p class="lead" style="text-color:black;">
        Your monthly spending(£{user.spending.totalAccountSpending}) has exceeded the budget(£{user.spending.budget})!<p>

        View more about your spending here: {url_for('main.homepage', _external=True)}
    """
    return msg


def budget_close_email(user):
    """
    Create a email message for the user.
    The email contains user's spending and his budget and tells the user that
    the spending is close to the budget
    :param user: user
    :return: email message
    """
    # create the email message
    msg = Message('Your Spending is Close to Budget', sender='noreply@gmail.com', recipients=[user.email])
    # '_external=True' here gives an absolute url rather than a relative url
    msg.html = f"""
        <header
            style="background-color:#033877; display:flex;">
            <img src="https://thebankly.com/wp-content/uploads/2019/01/getmyoffercapitalone.jpg" 
                class="img-fluid"
                alt="Capital One homepage"
                style="float:center; width:150px; height:45px; padding:30px;">
            <h1 style="text-align:center; color:white; padding:15px;">Capital One</h1>
        </header>
        <p class="lead" style="text-color:black;">
        Your spending(£{user.spending.totalAccountSpending}) is close to the budget(£{user.spending.budget})!<p>
        
        View more about your spending here: {url_for('main.homepage', _external=True)}
    """

    return msg


def balance_close_email(user, card):
    """
    Create a email message for the user.
    The email contains card's spending and its balance and tells the user that
    he/she is running out of money.
    :param user: user
    :return: email message
    """
    # create the email message
    msg = Message('Running out of money', sender='noreply@gmail.com', recipients=[user.email])
    # '_external=True' here gives an absolute url rather than a relative url
    msg.html = f"""
        <header
            style="background-color:#033877; display:flex;">
            <img src="https://thebankly.com/wp-content/uploads/2019/01/getmyoffercapitalone.jpg" 
                class="img-fluid"
                alt="Capital One homepage"
                style="float:center; width:150px; height:45px; padding:30px;">
            <h1 style="text-align:center; color:white; padding:15px;">Capital One</h1>
        </header>
        <p class="lead" style="text-color:black;">
            You are running out of money on Card: {card.card_name}
            <br>
            Total Spending: £{card.get_total_spending()}
            <br>
            Balance: £{card.balance}!
        <p>
    
        View more about your spending here: {url_for('main.homepage', _external=True)}
    """

    return msg


def report_email(user, start_date, end_date):
    """
    Create a email report for the user.
    The email contains a report.
    :param user:
    :return: email message
    """
    email_address = user.email
    msg = Message('Your Report is here', sender='noreply@gmail.com', recipients=[email_address])
    print("Trying to fetch all valid transactions...")
    transactions = utils.get_all_transactions(user, start_date, end_date)
    print("Transactions are fetched!")
    print("Trying to get all required data...")
    total_balance = utils.get_all_balance(user)
    total_spending = utils.get_total_spending(transactions)
    weekday_list = utils.get_weekday_spending(transactions)
    categories_list = utils.get_all_categories(transactions)
    print("Required data are got!")
    print("Trying to construct report content...")
    msg.html = f"""
        <header
            style="background-color:#033877; display:flex;">
            <img src="https://thebankly.com/wp-content/uploads/2019/01/getmyoffercapitalone.jpg" 
                class="img-fluid"
                alt="Capital One homepage"
                style="float:center; width:150px; height:45px; padding:30px;">
            <h1 style="text-align:center; color:white; padding:15px;">Financial Report</h1>
        </header>
        <p class="lead" style="text-color:black;">
            <p style="font-weight:bold;">{user.firstname} {user.lastname}<p>
            Date: from {start_date} to {end_date}
            <br><br>
            <p style="font-weight:bold;">Overview<p>
            Total expenditures: £{round(total_spending, 2)}
            <br>
            Current balance: £{round(total_balance, 2)}
            <br>
            <p style="font-weight:bold;">Average daily expenditures<p>
            Mondays: £{round(weekday_list.get('0', 0), 2)}
            <br>
            Tuesdays: £{round(weekday_list.get('1', 0), 2)}
            <br>
            Wednesdays: £{round(weekday_list.get('2', 0), 2)}
            <br>
            Thursdays: £{round(weekday_list.get('3', 0), 2)}
            <br>
            Fridays: £{round(weekday_list.get('4', 0), 2)}
            <br>
            Saturdays: £{round(weekday_list.get('5', 0), 2)}
            <br>
            Sundays: £{round(weekday_list.get('6', 0), 2)}
            <br>
            <p style="font-weight:bold;">Expenditures by category<p>
    """
    for key in categories_list:
        msg.html += f"""
                {key}: £{round(categories_list[key], 2)}
                <br>
        """
    msg.html += f"<p> View more about your spending here: {url_for('main.homepage', _external=True)}"
    print("Report content is constructed!")
    return msg


def category_budget_email(user, categorybudget, spending):
    """
    Create a email message for the user.
    The email contains user's spending within a category and its budget and tells the user that
    the spending has exceeded the budget for that category
    :param user: user
    :return: email message
    """
    msg = Message('Your Spending is Over Budget', sender='noreply@gmail.com', recipients=[user.email])
    print("Trying to construct the email...")
    msg.html = f"""
            <header
                style="background-color:#033877; display:flex;">
                <img src="https://thebankly.com/wp-content/uploads/2019/01/getmyoffercapitalone.jpg" 
                    class="img-fluid"
                    alt="Capital One homepage"
                    style="float:center; width:150px; height:45px; padding:30px;">
                <h1 style="text-align:center; color:white; padding:15px;">Capital One</h1>
            </header>
            <p class="lead" style="text-color:black;">
                Your monthly spending on {categorybudget.category} has exceeded your budget!
                <br>
                Monthly Spending on {categorybudget.category}: £{spending}
                <br>
                Monthly {categorybudget.category} Budget: £{categorybudget.budget}
            <p>

            View more about your spending here: {url_for('main.homepage', _external=True)}
        """

    return msg
