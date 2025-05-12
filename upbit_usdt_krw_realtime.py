import requests
import time
from datetime import datetime


def get_upbit_price():
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": "KRW-USDT"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and isinstance(data, list):
            return data[0]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def display_price_data(data):
    if not data:
        print("No data available")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trade_price = data.get('trade_price')
    prev_price = data.get('prev_closing_price')
    price_change = data.get('signed_change_rate')
    high_price = data.get('high_price')
    low_price = data.get('low_price')
    volume = data.get('acc_trade_volume_24h')

    if trade_price is None:
        print("Invalid data format")
        return

    change_percent = price_change * 100 if price_change else 0
    change_status = "↑" if change_percent >= 0 else "↓"

    print(f"\n[Upbit USDT-KRW] {timestamp}")
    print(f"当前价格: {trade_price:,.1f} KRW")  # 修改为保留1位小数
    print(f"24小时变化: {change_status}{abs(change_percent):.1f}%")  # 修改为保留1位小数
    print(f"24小时最高: {high_price:,.1f} KRW")  # 修改为保留1位小数
    print(f"24小时最低: {low_price:,.1f} KRW")  # 修改为保留1位小数
    print(f"24小时交易量: {float(volume):,.1f} USDT")  # 修改为保留1位小数


def main():
    print("启动 Upbit USDT-KRW 价格监控 (每5秒更新)...")
    print("按 Ctrl+C 停止程序")

    try:
        while True:
            data = get_upbit_price()
            display_price_data(data)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n程序已停止")


if __name__ == "__main__":
    main()