# Market Maker (Repo)

Janky simulator with bad code. This readme is for anyone who is interested in looking at this project or just browsing github.

Uses ZeroMQ for communication. Exchange used to simulate an order book. Publishes events with the user id (probably not how it works in reality, but just wanted to make it work).

First
```
cd src
```

# Exchange

An exchange is set up to execute incoming orders from users (traders). The exchange publishes events which may result in a change to the order book, and publishes the order book (prices/order amounts) whenever it changes.

To run the exhange:
```
python main_exchange.py
```

# Agents

Traders arrive following an exponential distribution.

To run the various agents.
```
python main_<agent_name>.py
```
## Noise Traders

Noise traders trade in a random direction with random order quantities and prices (configured to follow a normal distribution, with price following the mid price). Noise traders can be configured to randomly use limit (includes prices) or market orders (ignores prices).

## HODLer

A HODLer buys in one direction without the intention of selling (or vice versa). HODLers use market orders and the quantities of each order can be configured to follow a normal distribution, or trade some predetermined dollar amount.

## Informed Traders

An informed trader knows the theoretical value of an asset. If the bid is above the theoretical, they will likely sell, and if the ask is below the theoretical, they will likely buy. Informed traders can use either market or limit orders. The quantity increases linearly with respect to the trades EV (i.e. `abs[theo-(bid-or-ask)]`).

## Market Makers

A market maker quotes bids/asks (although not always as of the writing of this README). A market maker can skew their quotes depending on their position and max allocation (e.g. they may quote a lower bid and high ask relative to the market makers theoretical if the market maker is very long). Theoretical value is updated depending on the last trade price and volume against the previous theoretical price.

# Visualizations

## Public Order Book

The publically streamed order book contains at most 8 levels, and the in-order list of the amount quoted per order at each level.

To view the publically streamed order book:
```
python main_vis_public_book.py
```

## Last Trade Price

Last trade prices can be viewed at
```
python main_vis_stock_price.py
```

## Trader P/L

Each trader can be configured to view their P/L. Just modify the script and rerun.