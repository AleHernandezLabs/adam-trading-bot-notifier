from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, PositiveFloat, ValidationInfo
from typing import Optional, Literal, Final, TypedDict
import logging
import os
import html
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN: Final[str] = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID: Final[str] = os.getenv("TELEGRAM_CHAT_ID")
ENV: Final[str] = os.getenv("ENV", "local")
HOST: Final[str] = os.getenv("HOST", "0.0.0.0")
PORT: Final[int] = int(os.getenv("PORT", 8000))

# Initialize logging
def setup_logging():
    log_dir: Final[str] = "logs"
    if ENV == "local":
        os.makedirs(log_dir, exist_ok=True)
        log_filename = datetime.now().strftime(f"{log_dir}/log_%Y%m%d_%H%M%S.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    return logging.getLogger(__name__)

logger = setup_logging()

# Initialize Telegram Bot
def initialize_bot(token: str) -> Bot:
    logger.info("🔄 Initializing Telegram Bot...")
    bot_instance = Bot(token=token)
    logger.info("✅ Telegram Bot initialized successfully.")
    return bot_instance

bot = initialize_bot(TELEGRAM_TOKEN)

# Initialize FastAPI App
app = FastAPI(
    title="Adam Trading Bot Notifier",
    description="A high-quality API by AleHernándezLabs to send structured trade notifications to Telegram.",
    version="1.0.0",
    contact={
        "name": "Alejandro Exequiel Hernández Lara",
        "url": "https://alehernandezlabs.com",
        "email": "alejandro@alehernandezlabs.com",
        "phone": "+56 9 44889280"
    },
    license_info={
        "name": "AleHernándezLabs License",
        "url": "https://alehernandezlabs.com/license"
    },
    terms_of_service="https://alehernandezlabs.com/terms"
)

# Models
class HealthResponse(BaseModel):
    status: str = "OK"

class MessageRequest(BaseModel):
    message: str = Field(..., title="Message", description="Message to send to the Telegram bot")

class TradeData(TypedDict):
    side: Literal["BUY", "SELL"]
    crypto: str
    price: float
    quantity: float
    total_cost: float
    binance_fee_percentage: float
    binance_fee_amount: float
    net_total: float
    binance_order_id: str
    profit_loss_percentage: Optional[float]
    profit_loss_usdt: Optional[float]
    avg_buy_price: Optional[float]
    sell_price: Optional[float]

class TradeExecutionRequest(BaseModel):
    side: Literal["BUY", "SELL"]
    crypto: str = Field(..., min_length=1, description="Cryptocurrency symbol, e.g., BTC or ETH")
    price: PositiveFloat
    quantity: PositiveFloat
    total_cost: PositiveFloat
    binance_fee_percentage: PositiveFloat
    binance_fee_amount: PositiveFloat
    net_total: PositiveFloat
    binance_order_id: str
    profit_loss_percentage: Optional[float] = None
    profit_loss_usdt: Optional[float] = None
    avg_buy_price: Optional[float] = None
    sell_price: Optional[float] = None

    @field_validator("profit_loss_percentage", "profit_loss_usdt", "avg_buy_price", "sell_price")
    def validate_sell_fields(cls, v, info: ValidationInfo):
        if info.data["side"] == "SELL" and v is None:
            raise ValueError("This field is required for SELL transactions")
        return v

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up Adam Trading Bot Notifier API...")
    yield
    logger.info("🛑 Shutting down Adam Trading Bot Notifier API...")
    await bot.session.close()
    logger.info("🔒 Telegram Bot session closed successfully.")

app.router.lifespan_context = lifespan

# Healthcheck Endpoint
@app.get("/healthcheck", response_model=HealthResponse)
async def healthcheck():
    """Health check endpoint to ensure the API is running."""
    logger.info("✅ Healthcheck endpoint accessed.")
    return {"status": "OK"}

# Send Message Endpoint
@app.post("/send-message")
async def send_message(request: MessageRequest):
    """Send a custom message to the Telegram bot."""
    try:
        logger.info("📨 Attempting to send a custom message to Telegram...")
        message = html.escape(request.message)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
        logger.info("📤 Custom message sent successfully.")
        return {"status": "Message sent"}
    except TelegramAPIError as e:
        logger.error("❌ Failed to send custom message to Telegram: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send message to Telegram")

# Trade Execution Message Endpoint
@app.post("/trade-execution")
async def send_trade_execution(request: TradeExecutionRequest):
    """Send a structured trade execution message to the Telegram bot."""
    try:
        logger.info("📨 Preparing trade execution message for Telegram...")

        # Generate a well-aligned, friendly message format
        trade_message = f"""
<b>🚀 Trade Execution Alert</b>

<b>📝 Side:</b>           {request.side}
<b>💰 Crypto:</b>        {request.crypto}
<b>📉 Price:</b>         ${request.price:,.2f}
<b>📊 Quantity:</b>      {request.quantity} {request.crypto}
<b>💸 Total Cost:</b>    ${request.total_cost:,.2f}
<b>📈 Fee ({request.binance_fee_percentage}%):</b> ${request.binance_fee_amount:,.2f}
<b>💵 Net Total:</b>     ${request.net_total:,.2f}
<b>🆔 Order ID:</b>      {request.binance_order_id}
"""

        if request.side == "SELL":
            trade_message += f"""
<b>📈 Profit/Loss %:</b> {request.profit_loss_percentage:.2f}%
<b>💵 Profit/Loss:</b>   ${request.profit_loss_usdt:,.2f}
<b>📉 Avg Buy Price:</b> ${request.avg_buy_price:,.2f}
<b>💰 Sell Price:</b>    ${request.sell_price:,.2f}
"""

        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=trade_message.strip(), parse_mode="HTML")
        logger.info("📈 Trade execution message sent successfully.")
        return {"status": "Trade execution message sent"}
    except TelegramAPIError as e:
        logger.error("❌ Failed to send trade execution message to Telegram: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send trade execution message to Telegram")
    except ValueError as e:
        logger.error("⚠️ Validation error in trade execution data: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

# Main execution
if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=(ENV == "local"))
