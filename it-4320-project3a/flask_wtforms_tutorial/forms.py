"""Form class declaration."""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
import json
from os import path
from datetime import date
from wtforms.fields.html5 import DateField
from wtforms.validators import URL, DataRequired, Email, EqualTo, Length




def get_symbol():
    symbol = []
    basedir = path.abspath(path.dirname(__file__))
    with open(path.join(basedir, "symbols.json")) as jsonFile:
        symbols_list = json.load(jsonFile)

    for item in symbols_list:
        for key, value in item.items():
            if "ACT Symbol" in key:
                symbol.append(value)

    return [tuple((sym, sym)) for sym in symbol]



class StockForm(FlaskForm):
    
    symbol = SelectField("Choose Symbol",[DataRequired()], choices = get_symbol())

    chart_type = SelectField("Select Chart Type",[DataRequired()],
        choices=[
            ("1", "1. Bar"),
            ("2", "2. Line"),
        ],
    )

    time_series = SelectField("Select Time Series",[DataRequired()],
        choices=[
            ("1", "1. Intraday"),
            ("2", "2. Daily"),
            ("3", "3. Weekly"),
            ("4", "4. Monthly"),
        ],
    )

    start_date = DateField("Enter Start Date")
    end_date = DateField("Enter End Date")
    submit = SubmitField("Submit")



