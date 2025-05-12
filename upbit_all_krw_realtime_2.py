import requests
import time
from datetime import datetime
from texttable import Texttable


class UpbitKRWtoUSDTMonitor:
    def __init__(self):
        self.usdt_krw_price = None
        self.update_interval = 10  # 10秒更新一次
        self.display_count = 15  # 显示前15个交易量最大的交易对

    def get_all_krw_markets(self):
        """获取所有KRW交易对"""
        url = "https://api.upbit.com/v1/market/all"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return [m['market'] for m in response.json()
                    if m['market'].startswith('KRW-') and m['market'] != 'KRW-USDT']
        except Exception as e:
            print(f"⚠️ 获取交易对列表失败: {e}")
            return []

    def fetch_prices(self, markets):
        """批量获取价格数据"""
        url = "https://api.upbit.com/v1/ticker"
        try:
            results = []
            # 分批获取避免请求过大(每次最多10个)
            for i in range(0, len(markets), 10):
                params = {"markets": ",".join(markets[i:i + 10])}
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                results.extend(response.json())
            return results
        except Exception as e:
            print(f"⚠️ 获取价格数据失败: {e}")
            return None

    def clear_screen(self):
        """清空终端屏幕"""
        print("\033c", end="")

    def process_market_data(self, data):
        """处理市场数据并计算USDT计价"""
        processed = []
        for item in data:
            if not item or 'market' not in item:
                continue

            krw_price = item.get('trade_price', 0)
            usdt_price = krw_price / self.usdt_krw_price if self.usdt_krw_price else 0
            volume_krw = item.get('acc_trade_price_24h', 0)
            volume_usdt = volume_krw / self.usdt_krw_price if self.usdt_krw_price else 0
            change = item.get('signed_change_rate', 0) * 100

            processed.append({
                'market': item['market'].replace("KRW-", ""),
                'krw_price': krw_price,
                'usdt_price': usdt_price,
                'volume_usdt': volume_usdt,
                'change': change
            })

        # 按24h交易量(USDT)降序排序
        return sorted(processed, key=lambda x: x['volume_usdt'], reverse=True)

    def display_data(self, sorted_data):
        """显示处理后的数据"""
        self.clear_screen()

        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "r", "r", "r", "r"])
        table.set_cols_width([8, 12, 12, 10, 18])

        # 表头
        table.header(["交易对", "KRW价格", "USDT价格", "24h涨跌", "24h交易量(USDT)"])

        # 添加数据行
        for item in sorted_data[:self.display_count]:
            table.add_row([
                item['market'],
                f"{item['krw_price']:,.0f}",
                f"{item['usdt_price']:,.4f}",
                f"{item['change']:+.2f}%",
                f"{item['volume_usdt']:,.1f}"
            ])

        # 显示信息
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"📊 Upbit KRW交易对USDT计价 | 按交易量排序 | 更新时间: {now}")
        print(f"💵 基准汇率: 1 USDT = {self.usdt_krw_price:,.1f} KRW")
        print(f"🔄 每{self.update_interval}秒更新 | 显示前{self.display_count}个交易对")
        print(table.draw())
        print("🛑 按 Ctrl+C 停止监控")

    def run(self):
        print("🚀 启动Upbit KRW交易对USDT计价监控(按交易量排序)...")

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

                # 2. 获取并处理其他KRW交易对数据
                if self.usdt_krw_price:
                    market_data = self.fetch_prices(krw_markets)
                    if market_data:
                        processed_data = self.process_market_data(market_data)
                        self.display_data(processed_data)

                # 精确控制更新间隔
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n🛑 监控已停止")
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    # 安装依赖: pip install requests texttable
    monitor = UpbitKRWtoUSDTMonitor()
    monitor.run()