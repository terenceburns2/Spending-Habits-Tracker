from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Length, Regexp
from spendingtracker.models import Card
from ukmodulus import validate_number
from flask import flash
from flask_login import current_user


class AddCardForm(FlaskForm):
    """
    Used in 'add_card' page for users to add new card.
    It has:
        1. Card name
        2. Bank Sort Code
        3. Bank account number
        4. Submit Button
    Raise errors:
        1. If the account number is already taken in the 'Card' table
    """

    # Card name is necessary, i.e. nullable = False
    card_name = StringField('Card Name:', validators=[DataRequired(message='You must add a name'), Length(max=20, message='Please input no more than 20 characters')])
    sort_code = StringField('Sort Code:', validators=[DataRequired(), Regexp('^\d\d-\d\d-\d\d$', message='Please input sort code in valid format. e.g. 99-99-99')])
    account_number = StringField('Account Number:', validators=[Length(min=6, max=11)])
    submit = SubmitField('Submit')

    def validate_card_name(self, card_name):
        cards = Card.query.filter_by(user_id=current_user.id)
        for card in cards:
            if card_name.data == card.card_name:
                raise ValidationError('This card name is taken by your another card.')

    def validate_account_number(self, account_number):
        """
        It checks if the account number is already in db.
        :param account_number: Bank account number
        :return: If the card is already in the db, raise an validation error,
        but don't return anything.
        """
        card = Card.query.filter_by(account_number=account_number.data).first()
        if card:
            raise ValidationError('That card is taken. Please choose a different one.')

    def isCardValid(self):
        """
        It checks if the card added by the user is valid by using module 'ukmodulus'
        :return: True if the card is valid, false if the card is invalid.
        """
        if validate_number(self.sort_code.data, self.account_number.data) == False:
            flash(f'Please ensure you insert valid card details.', 'danger')
            return False
        return True
