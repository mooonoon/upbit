import requests
import time
from datetime import datetime

previous_rate = None


def get_exchange_rate():
    global previous_rate
    url = "https://api.frankfurter.app/latest?from=USD&to=KRW"
    # url = "https://ecos.bok.or.kr/api/StatisticSearch/YOUR_API_KEY/json/kr/1/1/036Y001/DD/USD"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_rate = data.get('rates', {}).get('KRW')

        # 计算变化率
        change = None
        if previous_rate and current_rate:
            change = (current_rate - previous_rate) / previous_rate * 100

        previous_rate = current_rate
        return current_rate, change
    except requests.exceptions.RequestException as e:
        print(f"获取汇率数据时出错: {e}")
        return None, None


def display_exchange_rate(rate, change):
    if rate is None:
        print("无法获取汇率数据")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[KRW-USD 汇率] {timestamp}")
    print(f"当前汇率: 1 USD = {rate:,.1f} KRW")

    if change is not None:
        change_status = "↑" if change >= 0 else "↓"
        print(f"较上次变化: {change_status}{abs(change):.2f}%")


def main():
    print("启动 KRW-USD 外汇汇率监控 (每5秒更新)...")
    print("按 Ctrl+C 停止程序")

    try:
        while True:
            rate, change = get_exchange_rate()
            display_exchange_rate(rate, change)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n程序已停止")


if __name__ == "__main__":
    main()