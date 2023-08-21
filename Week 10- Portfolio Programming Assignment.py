# Course: ICT 4370: Python Programming 
# Term: Summer 2023
# Program Name: Week 10 - Portfolio Programming Assignment
# Author: Marina 
# Date Written: August 20th, 2023

# Import libraries

import pandas as pd
import sqlite3
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json


# Define investor class
class Investor:
    # Add attributes
    def __init__(self, investor_id, name, address, phone_number):
        self.investor_id = investor_id
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.stocks = []
        self.bonds = []

    def add_bond(self, symbol, shares, purchase_price, current_value, purchase_date, coupon, yield_rate):
        bond = Bond(symbol, shares, purchase_price, current_value, purchase_date, coupon, yield_rate)
        self.bonds.append(bond)

# Define stock class
class Stock:
    # Add attributes
    def __init__(self, symbol, shares, purchase_price, current_value, purchase_date):
        self.symbol = symbol
        self.shares = shares
        self.purchase_price = purchase_price
        self.current_value = current_value
        self.purchase_date = purchase_date
    
    # Calculate earnings/loss
    def calculate_earnings_loss(self):
        return round((self.current_value - self.purchase_price) * self.shares, 2)
    # Calculate percentage yield/loss
    def calculate_percentage_yield_loss(self):
        return round(((self.current_value - self.purchase_price) / self.purchase_price) * 100, 2)
    # Calculate yearly earnings/loss
    def calculate_yearly_earnings_loss_rate(self):
        purchase_date = datetime.strptime(self.purchase_date, "%m/%d/%Y")
        current_date = datetime.now()
        days_difference = (current_date - purchase_date).days
        if days_difference == 0:
            return 0.0
        else:
            return round(((self.current_value - self.purchase_price) / self.purchase_price) / (days_difference / 365) * 100, 2)
# Define bond class
class Bond(Stock):
    # Add atributes
    def __init__(self, symbol, shares, purchase_price, current_value, purchase_date, coupon, yield_rate):
        super().__init__(symbol, shares, purchase_price, current_value, purchase_date)
        self.coupon = coupon
        self.yield_rate = yield_rate

def load_json_data(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)

def load_csv_data(csv_file_path):
    data = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data
# Calculate stock value by purchased date
def calculate_stock_values(stock_data, purchase_data):
    stock_info = {}
    for stock in stock_data:
        symbol = stock['Symbol']
        date = datetime.strptime(stock['Date'], "%d-%b-%y")
        close = stock['Close']
        if symbol not in stock_info:
            stock_info[symbol] = {'dates': [], 'value': []}
        stock_info[symbol]['dates'].append(date)
        stock_info[symbol]['value'].append(float(close))
    for purchase_data in purchase_data:
        symbol = purchase_data.get("SYMBOL", "")
        if symbol not in stock_info:
            print("Warning: Symbol", symbol, "not found in stock_info.")
            continue
        shares = float(purchase_data.get("NO_SHARES", 0))
        purchase_date = datetime.strptime(purchase_data.get("PURCHASE_DATE", ""), "%m/%d/%Y")
        stock_info[symbol]['value'] = [round(close * shares, 2) if date >= purchase_date else close for date, close in zip(stock_info[symbol].get('dates', []), stock_info[symbol].get('value', []))]
    return stock_info
# Chart to show stock values over time
def plot_line_chart(stock_values):
    plt.figure(figsize=(12, 6.75))
    for symbol, values in stock_values.items():
        sorted_dates, sorted_values = zip(*sorted(zip(values.get('dates', []), values.get('value', []))))
        plt.plot(sorted_dates, sorted_values, label=symbol)
    plt.xlabel('Date')
    plt.ylabel('Stock Value')
    plt.title('Stock Value Over Time')
    plt.legend()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.savefig('line_chart.png')
    plt.show()
# Chart to show average value of stocks
def plot_bar_chart(stock_values):
    symbols = list(stock_values.keys())
    avg_values = [sum(values.get('value', [])) / len(values.get('value', [])) for values in stock_values.values()]
    plt.figure(figsize=(10, 6))
    plt.bar(symbols, avg_values, color='blue')
    plt.xlabel('Stock Symbol')
    plt.ylabel('Average Stock Value')
    plt.title('Average Stock Value by Symbol')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('bar_chart.png')
    plt.show()
# Chart to show distribution of stocks by current value
def plot_pie_chart(stocks):
    labels = [stock.symbol for stock in stocks]
    sizes = [stock.current_value for stock in stocks]
    colors = plt.cm.Paired(range(len(stocks)))  
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.3))
    plt.title('Distribution of Stocks by Current Value')
    plt.tight_layout()
    plt.savefig('pie_chart.png')
    plt.show()


try:
    stock_df = pd.read_csv('/Users/myp3103/Desktop/Python/Lesson6_Data_Stocks.csv')
    stock_df['PURCHASE_DATE'] = stock_df['PURCHASE_DATE'].apply(lambda x: datetime.strptime(x, "%m/%d/%Y").strftime('%m/%d/%Y'))

    bond_df = pd.read_csv('/Users/myp3103/Desktop/Python/Lesson6_Data_Bonds.csv', parse_dates=['PURCHASE_DATE'])
    bob_smith = Investor(987643, "Bob Smith", "876 Marina Way", "(407)983-7532")
    for row in stock_df.itertuples():
        stock = Stock(row.SYMBOL, row.NO_SHARES, row.PURCHASE_PRICE, row.CURRENT_VALUE, row.PURCHASE_DATE)
        bob_smith.stocks.append(stock)
    for row in bond_df.itertuples():
        symbol = row.SYMBOL
        number_shares = row.NO_SHARES
        purchase_price = row.PURCHASE_PRICE
        current_cost = row.CURRENT_VALUE
        purchase_date = row.PURCHASE_DATE.strftime('%m/%d/%Y')
        coupon = float(row.Coupon)
        yield_bond = float(str(row.Yield).strip('%')) / 100
        purchase_id = int(row.PURCHASE_DATE.strftime('%Y%m%d'))
        bob_smith.add_bond(symbol, number_shares, purchase_price, current_cost, purchase_date, coupon, yield_bond)
    conn = sqlite3.connect('investor_database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS investors (investor_id INTEGER PRIMARY KEY, name TEXT, address TEXT, phone_number TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stocks (stock_id INTEGER PRIMARY KEY, investor_id INTEGER, symbol TEXT, shares INTEGER, purchase_price REAL, current_value REAL, purchase_date TEXT, FOREIGN KEY (investor_id) REFERENCES investors (investor_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bonds (bond_id INTEGER PRIMARY KEY, investor_id INTEGER, symbol TEXT, shares INTEGER, purchase_price REAL, current_value REAL, purchase_date TEXT, coupon REAL, yield_rate REAL, FOREIGN KEY (investor_id) REFERENCES investors (investor_id))''')
    cursor.execute('INSERT OR REPLACE INTO investors (investor_id, name, address, phone_number) VALUES (?, ?, ?, ?)', (bob_smith.investor_id, bob_smith.name, bob_smith.address, bob_smith.phone_number))
    conn.commit()
    for stock in bob_smith.stocks:
        cursor.execute('INSERT OR REPLACE INTO stocks (investor_id, symbol, shares, purchase_price, current_value, purchase_date) VALUES (?, ?, ?, ?, ?, ?)', (bob_smith.investor_id, stock.symbol, stock.shares, stock.purchase_price, stock.current_value, stock.purchase_date))
        conn.commit()
    for bond in bob_smith.bonds:
        cursor.execute('INSERT OR REPLACE INTO bonds (investor_id, symbol, shares, purchase_price, current_value, purchase_date, coupon, yield_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (bob_smith.investor_id, bond.symbol, bond.shares, bond.purchase_price, bond.current_value, bond.purchase_date, bond.coupon, bond.yield_rate))
        conn.commit()
    conn.close()
    with open("investor_report.txt", "w") as report_file:
        report_file.write("Investor Name: Bob Smith\n")
        report_file.write("Investor Address: 876 Marina Way\n")
        report_file.write("Investor Phone Number: (407)983-7532\n")
        report_file.write("------ Stocks ------\n")
        for stock in bob_smith.stocks:
            report_file.write(f"Stock Symbol: {stock.symbol}\n")
            report_file.write(f"Number of Shares: {stock.shares}\n")
            report_file.write(f"Purchase Price: ${stock.purchase_price}\n")
            report_file.write(f"Current Value: ${stock.current_value}\n")
            report_file.write(f"Purchase Date: {stock.purchase_date}\n")
            report_file.write(f"Earnings/Loss: ${stock.calculate_earnings_loss()}\n")
            report_file.write(f"Percentage Yield/Loss: {stock.calculate_percentage_yield_loss()}%\n")
            report_file.write(f"Yearly Earnings/Loss Rate: {stock.calculate_yearly_earnings_loss_rate()}%\n")
            report_file.write("----------------------------\n")
        report_file.write("------ Bonds ------\n")
        for bond in bob_smith.bonds:
            report_file.write(f"Bond Symbol: {bond.symbol}\n")
            report_file.write(f"Number of Shares: {bond.shares}\n")
            report_file.write(f"Purchase Price: ${bond.purchase_price}\n")
            report_file.write(f"Current Value: ${bond.current_value}\n")
            report_file.write(f"Purchase Date: {bond.purchase_date}\n")
            report_file.write(f"Coupon: {bond.coupon}\n")
            report_file.write(f"Yield: {bond.yield_rate*100}%\n")
            report_file.write("----------------------------\n")
    stock_data_file_path = '/Users/myp3103/Desktop/Python/Week8Programming Assignment/AllStocks.json'
    stock_data = load_json_data(stock_data_file_path)
    stocks_values = calculate_stock_values(stock_data, stock_df.to_dict('records'))
    plot_line_chart(stocks_values)
    plot_bar_chart(stocks_values)
    plot_pie_chart(bob_smith.stocks)

# Exception for file not found
except FileNotFoundError:
    print("An error occurred while reading the input files.")
