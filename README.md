Janky simulator with bad code.

Uses ZeroMQ for communication. Exchange used to simulate an order book. Publishes events with the user id (probably not how it works in reality, but just wanted to make it work).

```
python exchange/main_exchange.py
```

```
python visualizations/order_book/main_public.py
```

```
python agents/main_noise_trader.py
```