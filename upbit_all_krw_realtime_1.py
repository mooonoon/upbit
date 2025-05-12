import requests
import time
from datetime import datetime
from texttable import Texttable  # 用于创建美观的表格输出
# upbit交易量前100 每60s更新

class UpbitKRWtoUSDTMonitor:
    def __init__(self):
        self.usdt_krw_price = None
        self.update_interval = 60  # 10秒更新一次
        self.max_display = 100  # 最多显示10个主要交易对

    def get_all_krw_markets(self):
        """获取所有KRW交易对"""
        url = "https://api.upbit.com/v1/market/all"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return [m['market'] for m in response.json() if
                    m['market'].startswith('KRW-') and m['market'] != 'KRW-USDT']
        except Exception as e:
            print(f"⚠️ 获取交易对列表失败: {e}")
            return []

    def fetch_prices(self, markets):
        """批量获取价格数据"""
        url = "https://api.upbit.com/v1/ticker"
        try:
            # 分批获取避免请求过大
            results = []
            for i in range(0, len(markets), 10):  # Upbit API每次最多查询10个
                params = {"markets": ",".join(markets[i:i + 10])}
                response = requests.get(url, params=params, timeout=60)
                response.raise_for_status()
                results.extend(response.json())
            return results
        except Exception as e:
            print(f"⚠️ 获取价格数据失败: {e}")
            return None

    def clear_screen(self):
        """清空终端屏幕"""
        print("\033c", end="")  # 跨平台的清屏方法

    def display_market_data(self, data):
        """显示市场数据"""
        self.clear_screen()

        # 获取当前时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 创建表格
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "r", "r", "r", "r"])
        table.set_cols_width([10, 15, 15, 15, 15])

        # 表头
        table.header(["交易对", "KRW价格", "USDT价格", "24h涨跌幅", "24h交易量(USDT)"])

        # 按交易量排序并选取前N个
        sorted_data = sorted(data, key=lambda x: x.get('acc_trade_price_24h', 0), reverse=True)
        top_markets = sorted_data[:self.max_display]

        for item in top_markets:
            market = item['market'].replace("KRW-", "")
            krw_price = item.get('trade_price', 0)
            usdt_price = krw_price / self.usdt_krw_price if self.usdt_krw_price else 0
            change = (item.get('signed_change_rate', 0) * 100)
            change_str = f"{change:+.2f}%"
            volume_usdt = item.get('acc_trade_price_24h', 0) / self.usdt_krw_price if self.usdt_krw_price else 0

            table.add_row([
                market,
                f"{krw_price:,.0f}",
                f"{usdt_price:,.4f}",
                change_str,
                f"{volume_usdt:,.1f}"
            ])

        # 显示信息
        print(f"🔄 Upbit KRW交易对USDT计价监控 | 更新时间: {now}")
        print(f"💱 基准汇率: 1 USDT = {self.usdt_krw_price:,.1f} KRW")
        print(f"📊 显示交易量前{self.max_display}的交易对 (每{self.update_interval}秒更新)")
        print(table.draw())
        print("🛑 按 Ctrl+C 停止监控")

    def run(self):
        print("🚀 启动Upbit KRW交易对USDT计价监控...")

        # 首次获取所有KRW交易对
        krw_markets = self.get_all_krw_markets()
        if not krw_markets:
            print("无法获取任何KRW交易对，请检查网络连接")
            return

        try:
            while True:
                start_time = time.time()

                # 1. 获取USDT-KRW汇率
                usdt_data = self.fetch_prices(["KRW-USDT"])
                if usdt_data and len(usdt_data) > 0:
                    self.usdt_krw_price = usdt_data[0].get('trade_price')

                # 2. 获取其他KRW交易对数据
                if self.usdt_krw_price:
                    market_data = self.fetch_prices(krw_markets)
                    if market_data:
                        self.display_market_data(market_data)

                # 计算剩余等待时间
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n🛑 监控已停止")
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    # 安装必要的库: pip install requests texttable
    monitor = UpbitKRWtoUSDTMonitor()
    monitor.run()