import ccxt
import time
from datetime import datetime
from texttable import Texttable


class UpbitKRWMarketMonitor:
    def __init__(self):
        self.exchange = ccxt.upbit({
            'enableRateLimit': True,  # 启用速率限制
            'timeout': 15000,  # 15秒超时
        })
        self.update_interval = 60  # 60秒更新一次
        self.max_display = 100  # 最多显示100个交易对
        self.usdt_krw_rate = None  # USDT-KRW汇率

    def get_all_krw_markets(self):
        """获取所有KRW交易对"""
        try:
            self.exchange.load_markets()
            return [symbol for symbol in self.exchange.symbols
                    if symbol.endswith('/KRW') and symbol != 'USDT/KRW']
        except Exception as e:
            print(f"⚠️ 获取交易对列表失败: {e}")
            return []

    def fetch_tickers(self, symbols):
        """批量获取行情数据"""
        try:
            # CCXT原生支持批量获取ticker
            return self.exchange.fetch_tickers(symbols)
        except Exception as e:
            print(f"⚠️ 获取行情数据失败: {e}")
            return None

    def get_usdt_krw_rate(self):
        """获取USDT-KRW汇率"""
        try:
            ticker = self.exchange.fetch_ticker('USDT/KRW')
            return ticker['last']
        except Exception as e:
            print(f"⚠️ 获取USDT汇率失败: {e}")
            return None

    def clear_screen(self):
        """清空终端屏幕"""
        print("\033c", end="")

    def process_market_data(self, tickers):
        """处理市场数据"""
        processed = []
        for symbol, ticker in tickers.items():
            if symbol == 'USDT/KRW':
                continue

            krw_price = ticker.get('last')
            volume_krw = ticker.get('quoteVolume', 0)  # KRW计价交易量
            change = ticker.get('percentage', 0)  # 百分比变化

            processed.append({
                'market': symbol.replace('/KRW', ''),
                'krw_price': krw_price,
                'usdt_price': krw_price / self.usdt_krw_rate if self.usdt_krw_rate else 0,
                'volume_usdt': volume_krw / self.usdt_krw_rate if self.usdt_krw_rate else 0,
                'change': change
            })

        # 按24h交易量(USDT)降序排序
        return sorted(processed, key=lambda x: x['volume_usdt'], reverse=True)

    def display_market_data(self, processed_data):
        """显示市场数据"""
        self.clear_screen()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 创建表格
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "r", "r", "r", "r"])
        table.set_cols_width([10, 15, 15, 10, 18])

        # 表头
        table.header(["交易对", "KRW价格", "USDT价格", "24h涨跌", "24h交易量(USDT)"])

        # 添加数据行
        for item in processed_data[:self.max_display]:
            table.add_row([
                item['market'],
                f"{item['krw_price']:,.0f}" if item['krw_price'] else 'N/A',
                f"{item['usdt_price']:,.4f}" if item['usdt_price'] else 'N/A',
                f"{item['change']:+.2f}%",
                f"{item['volume_usdt']:,.1f}" if item['volume_usdt'] else 'N/A'
            ])

        # 显示信息
        print(f"📊 Upbit KRW交易对实时监控 (CCXT) | 更新时间: {now}")
        print(f"💱 基准汇率: 1 USDT = {self.usdt_krw_rate:,.1f} KRW" if self.usdt_krw_rate else "💱 基准汇率: 未获取")
        print(f"🔄 每{self.update_interval}秒更新 | 显示前{self.max_display}个交易对")
        print(table.draw())
        print("🛑 按 Ctrl+C 停止监控")

    def run(self):
        print("🚀 启动Upbit KRW交易对实时监控(使用CCXT)...")

        krw_markets = self.get_all_krw_markets()
        if not krw_markets:
            print("无法获取KRW交易对列表")
            return

        try:
            while True:
                start_time = time.time()

                # 1. 获取USDT-KRW汇率
                self.usdt_krw_rate = self.get_usdt_krw_rate()

                # 2. 获取所有KRW交易对数据
                tickers = self.fetch_tickers(krw_markets)

                if tickers:
                    processed_data = self.process_market_data(tickers)
                    self.display_market_data(processed_data)

                # 精确控制更新间隔
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n🛑 监控已停止")
        except Exception as e:
            print(f"❌ 发生错误: {e}")
        finally:
            self.exchange.close()


if __name__ == "__main__":
    # 安装依赖: pip install ccxt texttable
    monitor = UpbitKRWMarketMonitor()
    monitor.run()