Janky simulator with bad code.

Uses ZeroMQ for communication. Exchange used to simulate an order book. Publishes events with the user id (probably not how it works in reality, but just wanted to make it work).

First
```
cd src
```

To run the exhange:
```
python main_exchange.py
```

To view the publically streamed order book:
```
python main_vis_public_book.py
```

Noise traders can be configured to randomly use limit or market orders.

To run the various agents.
```
python main_noise_trader.py
python main_market_maker.py
```