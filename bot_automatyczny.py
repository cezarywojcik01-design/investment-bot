import yfinance as yf
from telegram import Bot
import os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# DODAJ TO - debugowanie
print(f"Token: {TOKEN[:10]}...")
print(f"Chat ID: {CHAT_ID}")

def get_price(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d")
    
    current_price = hist['Close'].iloc[-1]
    previous_close = hist['Open'].iloc[-1]
    change = current_price - previous_close
    change_percent = (change / previous_close) * 100
    
    return {
        'symbol': symbol,
        'price': current_price,
        'change': change,
        'change_percent': change_percent
    }

def send_update():
    bot = Bot(token=TOKEN)
    
    symbols = ["BTC-USD", "AAPL", "TSLA"]
    
    message = f"📊 **RAPORT - {datetime.now().strftime('%H:%M')}**\n\n"
    
    for symbol in symbols:
        try:
            data = get_price(symbol)
            emoji = "🟢" if data['change'] >= 0 else ""
            message += f"{emoji} **{data['symbol']}**: ${data['price']:.2f} ({data['change_percent']:+.2f}%)\n"
        except Exception as e:
            message += f"❌ {symbol}: Błąd\n"
            print(f"Błąd dla {symbol}: {e}")
    
    print(f"Wysyłam wiadomość do: {CHAT_ID}")
    print(f"Treść: {message}")
    
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
    print("✅ Wysłano raport!")

if __name__ == "__main__":
    send_update()
