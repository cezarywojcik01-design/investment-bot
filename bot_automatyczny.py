import asyncio
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from telegram import Bot
import os
from datetime import datetime
import pytz
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_price_and_rsi(symbol):
    """Pobiera cenę i oblicza RSI"""
    try:
        stock = yf.Ticker(symbol)
        
        # Pobierz dane historyczne (potrzebne do RSI)
        df = stock.history(period="2mo")
        
        # Oblicz RSI (14-okresowy)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        current_price = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[-2]
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        current_rsi = df['RSI'].iloc[-1]
        
        # Generuj sygnał na podstawie RSI
        if current_rsi < 30:
            signal = "🟢 KUPUJ"
            signal_desc = "(wyprzedanie - potencjalna okazja)"
        elif current_rsi > 70:
            signal = "🔴 SPRZEDAWAJ"
            signal_desc = "(wykupienie - uważaj)"
        else:
            signal = "🟡 TRZYMAJ"
            signal_desc = "(rynek neutralny)"
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change': change,
            'change_percent': change_percent,
            'rsi': current_rsi,
            'signal': signal,
            'signal_desc': signal_desc,
            'error': None
        }
    except Exception as e:
        return {
            'symbol': symbol,
            'error': str(e)
        }

async def send_update():
    """Wysyła raport z analizą techniczną"""
    bot = Bot(token=TOKEN)
    
    # Lista spółek do analizy
    symbols = ["BTC-USD", "ETH-USD", "AAPL", "TSLA"]
    
    message = f"📊 **RAPORT INWESTYCYJNY**\n"
    message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    message += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for symbol in symbols:
        data = get_price_and_rsi(symbol)
        
        if data['error']:
            message += f"❌ **{symbol}**: Błąd danych\n\n"
            continue
        
        emoji = "🟢" if data['change'] >= 0 else "🔴"
        
        message += f"{emoji} **{data['symbol']}**\n"
        message += f"💰 Cena: ${data['price']:.2f}\n"
        message += f"📈 Zmiana: {data['change_percent']:+.2f}%\n"
        message += f"📉 RSI: {data['rsi']:.1f}\n"
        message += f"🎯 {data['signal']} {data['signal_desc']}\n"
        message += f"\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    message += f"💡 **Legenda RSI:**\n"
    message += f"• RSI < 30 = Wyprzedanie (kupno)\n"
    message += f"• RSI > 70 = Wykupienie (sprzedaż)\n"
    message += f"• RSI 30-70 = Neutralnie\n"
    
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
    print("✅ Wysłano raport z analizą!")

if __name__ == "__main__":
    asyncio.run(send_update())
