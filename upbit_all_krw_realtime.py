import requests
import time
from datetime import datetime
# upbit上币顺序展示

class UpbitKRWtoUSDTConverter:
    def __init__(self, update_interval=5):
        self.update_interval = update_interval
        self.usdt_krw_price = None

    def get_all_krw_markets(self):
        """获取所有KRW交易对"""
        url = "https://api.upbit.com/v1/market/all"
        try:
            response = requests.get(url)
            response.raise_for_status()
            markets = response.json()
            return [market['market'] for market in markets if market['market'].startswith('KRW-')]
        except Exception as e:
            print(f"获取交易对列表失败: {e}")
            return []

    def get_usdt_krw_price(self):
        """获取USDT-KRW价格"""
        url = "https://api.upbit.com/v1/ticker"
        params = {"markets": "KRW-USDT"}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list):
                return data[0].get('trade_price')
            return None
        except Exception as e:
            print(f"获取USDT价格失败: {e}")
            return None

    def get_market_prices(self, markets):
        """批量获取多个交易对价格"""
        url = "https://api.upbit.com/v1/ticker"
        params = {"markets": ",".join(markets)}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取市场价格失败: {e}")
            return []

    def convert_to_usdt(self, krw_price):
        """将KRW价格转换为USDT价格"""
        if self.usdt_krw_price and krw_price:
            return krw_price / self.usdt_krw_price
        return None

    def display_results(self, data):
        """显示转换结果"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[Upbit KRW交易对USDT计价] {timestamp}")
        print(f"基准汇率: 1 USDT = {self.usdt_krw_price:,.1f} KRW")
        print("-" * 60)
        print(f"{'交易对':<10}{'KRW价格':>15}{'USDT价格':>15}{'24h交易量(USDT)':>20}")
        print("-" * 60)

        for item in data:
            market = item['market'].replace("KRW-", "")
            krw_price = item.get('trade_price', 0)
            usdt_price = self.convert_to_usdt(krw_price)
            volume_krw = item.get('acc_trade_price_24h', 0)
            volume_usdt = volume_krw / self.usdt_krw_price if self.usdt_krw_price else 0

            print(f"{market:<10}{krw_price:>15,.1f}{usdt_price:>15,.4f}{volume_usdt:>20,.2f}")

    def run(self):
        print("启动Upbit KRW交易对USDT计价监控...")
        print("按Ctrl+C停止程序")

        krw_markets = self.get_all_krw_markets()
        if not krw_markets:
            print("无法获取KRW交易对列表")
            return

        # 移除USDT本身，避免重复
        krw_markets = [m for m in krw_markets if m != "KRW-USDT"]

        try:
            while True:
                # 先获取USDT-KRW汇率
                self.usdt_krw_price = self.get_usdt_krw_price()

                if self.usdt_krw_price:
                    # 分批获取所有KRW交易对价格（避免一次性请求太多）
                    batch_size = 10  # Upbit API单次请求限制
                    all_data = []
                    for i in range(0, len(krw_markets), batch_size):
                        batch = krw_markets[i:i + batch_size]
                        batch_data = self.get_market_prices(batch)
                        all_data.extend(batch_data)

                    if all_data:
                        self.display_results(all_data)

                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            print("\n监控已停止")


if __name__ == "__main__":
    monitor = UpbitKRWtoUSDTConverter(update_interval=5)
    monitor.run()