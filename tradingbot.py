from lumibot.brokers.alpaca import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from datetime import datetime
from alpaca_trade_api import REST
from datetime import datetime, timedelta


base_url = "https://paper-api.alpaca.markets"

alpaca_creds = {
    "API_KEY": "PKX4OMBCODAD8SP5VR3C",
    "API_SECRET": "DSolELrmvUubdUiWKnwwM2oBHDb49vEjAkxYXDgI",
    "PAPER": True
}

class mltrader(Strategy):
    def initialize(self, Symbol="SPY", cash_at_risk: float = 0.5):
        self.Symbol = Symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api=REST(base_url=base_url,key_id="PKX4OMBCODAD8SP5VR3C",secret_key="DSolELrmvUubdUiWKnwwM2oBHDb49vEjAkxYXDgI")
    def getDates(self):
        today=self.get_datetime()
        three_days_prior=today-Timedelta(days=3)
        return today.strafttime('%Y-%m-%d'),three_days_prior.strafttime('%Y-%m-%d')
    
    def getnews(self):
        today,three_days_prior=self.get_dates()
        news=self.api.get_news(symbol=self.symbol,start=three_days_prior,end=today)    
        news=[ev.__dict__["_raw"]["headline"]for ev in news]
    
    
    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.Symbol)  # Fixed typo here
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

def on_trading_iteration(self):
    cash, last_price, quantity = self.position_sizing()
    order = None  # Initialize order variable
    print("Data used for backtest:")
    print(f"Symbol: {self.Symbol}, Cash: {cash}, Last Price: {last_price}, Quantity: {quantity}")

    if cash > last_price:
        if self.last_trade is None:
            news=self.get_news()
            print(news)
            order = self.create_order(
                self.Symbol,
                quantity,
                "buy",
                type="bracket",
                take_profit_price=last_price * 0.80,
                stop_loss_price=last_price * 1.05
            )
            self.last_trade = "buy"

    # Check if order is not None before submitting
    if order is not None:
        self.submit_order(order)



start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31) 
broker = Alpaca(alpaca_creds)
strategy = mltrader(name='mlstrat', broker=broker, parameter={"Symbol": "SPY", "cash_at_risk": 0.5})
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"Symbol": "SPY"}
)
