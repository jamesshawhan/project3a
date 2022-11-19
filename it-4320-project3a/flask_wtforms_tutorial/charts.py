
from os import environ
import requests
from json import JSONDecodeError
import requests
from datetime import datetime
from datetime import date
import pygal


def get_date(date_str: str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise Exception("invalid date")
    else:
        return date

class StockData:
    def __init__(self, stock_symbol: str, requested_function: int, user_start_date, user_end_date):
        self.__API_KEY = environ.get("API_KEY")
        self.__URL = environ.get("API_URL")
        self.__params_dictionary = {"apikey" : self.__API_KEY}
        self.__stock_symbol = stock_symbol
        self.__start_date = get_date(user_start_date)
        self.__end_date = get_date(user_end_date)

        if requested_function != 1 and self.__start_date > self.__end_date:
            raise Exception("The end date must be greater than or equal to the start date.")

        if requested_function == 1:
            self.__requested_function = "INTRADAY"
            self.__key_name = f"Time Series ({self.__interval})"
        elif requested_function == 2:
            self.__requested_function = "DAILY_ADJUSTED"
            self.__key_name = "Time Series (Daily)"
        elif requested_function == 3:
            self.__requested_function = "WEEKLY"
            self.__key_name = "Weekly Time Series"
        else:
            self.__requested_function = "MONTHLY"
            self.__key_name = "Monthly Time Series"

        self.__params_dictionary.update({"function" : f"TIME_SERIES_{self.__requested_function}", "symbol" : self.__stock_symbol})
        if self.__requested_function == "INTRADAY":
            self.__params_dictionary.update({"interval" : self.__interval})

        self.data_dictionary = self.__get_data()

    def __validate_stock_symbol(self, stock_symbol: str):
        try:
            self.__params_dictionary.update({"function" : "SYMBOL_SEARCH", "keywords" : stock_symbol})
            api_response = requests.get(self.__URL, params=self.__params_dictionary)
        except:
            raise Exception("The api is not available at the given moment.")
        else:
            if api_response.ok:
                if 'Error Message' in api_response.text:
                    self.__handle_API_response_errors(api_response)
                else:
                    try:            
                        response_dictionary = api_response.json()
                    except JSONDecodeError:
                        raise Exception("JSON decoding error")
                    else:
                        search_list = response_dictionary.get("bestMatches")
                        for search_dictionary in search_list:
                            if stock_symbol in search_dictionary.values():
                                return stock_symbol
                            else:
                                raise Exception(f"{stock_symbol}: this isn't a valid symbol.")
    
    def __get_data(self):
        data_dictionary = {}
        try:
            api_response = requests.get(self.__URL, params=self.__params_dictionary)
        except:
            raise Exception("The api is not available at the given moment.")
        else:
            if api_response.ok:

                if 'Error Message' in api_response.text:
                    self.__handle_API_response_errors(api_response)
                else:
                    try:
                        data_dictionary = self.__filter_API_response(api_response)
                    except Exception as ex:
                        raise Exception(ex)
            else:
                raise Exception(f"status code: \"{api_response.status_code}.\"")
        return data_dictionary

    def __handle_API_response_errors(self, api_response: requests.Response):
        try:
            response_dictionary = api_response.json()
        except JSONDecodeError:
            raise Exception("JSON decoding error")
        else:
            error_msg = response_dictionary.get('Error Message')
            if error_msg != None:
                raise Exception(error_msg)

    def __filter_API_response(self, api_response: requests.Response):
        filtered_dictionary = {}
        try:            
            response_dictionary = api_response.json()
        except JSONDecodeError:
            raise Exception("JSON decoding error")

        data_dictionary = response_dictionary.get(self.__key_name)
        if data_dictionary != None:
            for key, value in data_dictionary.items():
                if self.__requested_function != "INTRADAY":
                    retrieved_date = datetime.strptime(key, "%Y-%m-%d")
                    if retrieved_date >= self.__start_date and retrieved_date <= self.__end_date:
                        filtered_dictionary.update({key : value})
                else:
                    filtered_dictionary.update({key : value})
        else:
            raise Exception("The api is not available at the given moment."666)
        return filtered_dictionary

class StockChart:
    def __init__(self, symbol, chart_type, start_date, end_date, stock_data):
        self.symbol = symbol
        self.chart_type = chart_type
        self.start_date = start_date
        self.end_date = end_date
        self.stock_data = stock_data
        self.date_list = []
        self.open_list = []
        self.close_list = []
        self.high_list = []
        self.low_list = []
        self.__populate_chart_lists()

    def __populate_chart_lists(self):
        for key, value in self.stock_data.data_dictionary.items():
            self.date_list.append(key)
            for datapoint_key, datapoint_value in value.items():
                if "open" in datapoint_key:
                    datapoint_number = float(datapoint_value)
                    self.open_list.append(datapoint_number)
                if "adjusted" in datapoint_key:
                    datapoint_number = float(datapoint_value)
                    self.close_list.append(datapoint_number)
                if "high" in datapoint_key:
                    datapoint_number = float(datapoint_value)
                    self.high_list.append(datapoint_number)
                if "low" in datapoint_key:
                    datapoint_number = float(datapoint_value)
                    self.low_list.append(datapoint_number)

    def get_chart(self):
        self.date_list.reverse()
        if self.chart_type == 1:
            chart = pygal.Bar(x_label_rotation=45)
        else:
            chart = pygal.Line(x_label_rotation=45)
        chart.title = f"Stock Data for {self.symbol}: 6{self.start_date} to {self.end_date}"
        chart.x_labels = self.date_list
        chart.add("Open", self.open_list)
        chart.add("High", self.high_list)
        chart.add("Low", self.low_list)
        chart.add("Close", self.close_list)
        return chart.render_data_uri()