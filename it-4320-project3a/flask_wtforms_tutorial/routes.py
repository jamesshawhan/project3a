from flask import current_app as app
from flask import redirect, render_template, url_for, request, flash

from .forms import StockForm
from .charts import *


@app.route("/", methods=['GET', 'POST'])
@app.route("/stocks", methods=['GET', 'POST'])
def stocks():
    
    form = StockForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            symbol = request.form['symbol']
            chart_type = request.form['chart_type']
            time_series = request.form['time_series']
            start_date = request.form['start_date']
            end_date = request.form['end_date']   
            try:
                stock_data = StockData(symbol, int(time_series), start_date, end_date)
            except Exception as ex:
                err = f"error: {ex}"
                chart = None
            else:
                if not stock_data.data_dictionary.items():
                    err = "There was no data available for the time chosen"
                    chart = None
                else:
                    err = None
                    stock_chart = StockChart(symbol, int(chart_type), start_date, end_date, stock_data)
                    chart = stock_chart.get_chart()


            return render_template("stock.html", form=form, template="form-template", err = err, chart = chart)
    
    
    return render_template("stock.html", form=form, template="form-template")
