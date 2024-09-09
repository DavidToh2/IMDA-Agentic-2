import yfinance as yf
from datetime import datetime, timedelta

# Define ticker symbol
ticker = "NVDA"

# Calculate start and end dates for the past month
start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
end_date = datetime.today().strftime("%Y-%m-%d")

# Retrieve historical stock price data
nvda = yf.Ticker(ticker)
data = nvda.history(start=start_date, end=end_date)["Close"]

# Calculate performance metrics
paste_month_price = data[0]
percent_change = ((data[-1] / paste_month_price) - 1) * 100
cumulative_return = (data / paste_month_price).cumsum() * 100

# Retrieve percentage change for previous month
previous_month_start = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
previous_data = nvda.history(start=previous_month_start, end=start_date)["Close"]
previous_percent_change = ((previous_data[-1] / previous_data[0]) - 1) * 100

# Print results
print(f"Today's date: {datetime.today().strftime('%Y-%m-%d')}")
print(f"NVDA price one month ago: ${paste_month_price:.2f}")
print(f"Current NVDA price: ${data[-1]:.2f}")
print(f"What happened over the past month? \nPercent change: {percent_change:.2f}%")
print(f"Cumulative return over the past month: {cumulative_return[-1]:.2f}%")
print(f"\nOne month ago vs two months ago percent change: {previous_percent_change:.2f}%")