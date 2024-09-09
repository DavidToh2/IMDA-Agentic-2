import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Retrieve historical prices
nvidia = yf.Ticker("NVDA")
historical_prices = nvidia.history(period="1mo", interval="1d")['Close']

# Retrieve today's price
current_price = nvidia.last_price

print(f"Today's closing price: ${current_price:.2f}")

# Calculate daily returns
historical_prices['Returns'] = historical_prices.pct_change()

# Calculate cumulative return using CAGR
n_days = len(historical_prices)
cumulative_return = (1 + historical_prices['Returns'].mean()) ** n_days - 1

print(f"Cumulative return over the past month: {cumulative_return * 100:.2f}%")

# Visualize the historical prices
plt.plot(historical_prices.index, historical_prices['Close'])
plt.title('Nvidia Stock Prices (Past Month)')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.grid(True)
plt.show()

blog_content = """
# Nvidia Stock Performance Analysis - Past Month

## Introduction
Nvidia Corporation, a leading manufacturer of graphics processing units (GPUs) for gaming and professional markets, has been a focus of investors due to its significant role in the tech industry. Let's analyze its stock price performance over the past month.

## Stock Price Performance

- **Today's Closing Price**: ${current_price:.2f}
- **Cumulative Return Over the Past Month**: {cumulative_return * 100:.2f}%

![Nvidia Stock Prices (Past Month)]({plt.show().svg})
"""

with open('nvidia_blog.md', 'w') as f:
    f.write(blog_content)