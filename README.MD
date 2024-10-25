# 📈 Adam Trading Bot Notifier

**Adam Trading Bot Notifier** is an API developed by **AleHernándezLabs** that allows you to send detailed notifications
about trade executions to a Telegram bot. This API helps users monitor cryptocurrency transactions in real-time
through structured alerts.

## ✨ Features

- **📬 Trade Notifications**: Sends detailed trade alerts displaying essential information such as trade side,
  cryptocurrency, price, quantity, total cost, fee, and net total.
- **💬 Telegram Integration**: Uses `aiogram` to interact with a Telegram bot, ensuring that messages are
  structured with icons and emojis for a user-friendly experience.
- **🛠️ Modular Code**: Clean and organized codebase, with easy-to-modify message templates.
- **📜 Logging**: In local mode, logs are stored in a `logs` directory, making it easy to track API activity
  and errors.

## 🛠️ Requirements

- **Python 3.8+**
- Install dependencies from `requirements.txt`

## 🚀 Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:AleHernandezLabs/adam-trading-bot-notifier.git
   cd adam-trading-bot-notifier
   ```

2. (Optional) Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file in the root directory with the following variables:

   ```plaintext
   TELEGRAM_TOKEN=your_telegram_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ENV=local  # Change to "production" for production environment
   ```

## ▶️ Running the API

To start the API in development mode:

```bash
uvicorn main:app --reload
```

The API will run at `http://127.0.0.1:8000`.

## 📌 Endpoints

### Health Check

- **Description**: Checks if the API is running.
- **Method**: `GET`
- **URL**: `/healthcheck`

### Send Message

- **Description**: Sends a custom message to the Telegram bot.
- **Method**: `POST`
- **URL**: `/send-message`
- **Body**:

  ```json
  {
    "message": "Your custom message here"
  }
  ```

### Trade Execution Message

- **Description**: Sends a structured trade execution notification to the Telegram bot.
- **Method**: `POST`
- **URL**: `/trade-execution`
- **Example Body for BUY**:

  ```json
  {
    "side": "BUY",
    "crypto": "BTC",
    "price": 50000.0,
    "quantity": 0.01,
    "total_cost": 500.0,
    "binance_fee_percentage": 0.1,
    "binance_fee_amount": 0.5,
    "net_total": 499.5,
    "binance_order_id": "12345ABC"
  }
  ```

- **Example Body for SELL**:

  ```json
  {
    "side": "SELL",
    "crypto": "BTC",
    "price": 52000.0,
    "quantity": 0.01,
    "total_cost": 520.0,
    "binance_fee_percentage": 0.1,
    "binance_fee_amount": 0.52,
    "net_total": 519.48,
    "binance_order_id": "12345DEF",
    "profit_loss_percentage": 4.0,
    "profit_loss_usdt": 19.48,
    "avg_buy_price": 50000.0,
    "sell_price": 52000.0
  }
  ```

## 🔧 Production Configuration

For a production environment, set the `ENV` variable in `.env` to `production` to disable local logging.

## 📁 Logging

In **local mode** (`ENV=local`), logs are stored in the `logs/` directory with a timestamp in the filename.
Logs include details of API activities and errors, aiding in troubleshooting and monitoring.

## 📝 Contribution

Contributions are welcome! Please feel free to open an issue or submit a pull request for any improvements.

## 📜 License

**Adam Trading Bot Notifier** is licensed under the MIT License. See the `LICENSE` file for more information.
