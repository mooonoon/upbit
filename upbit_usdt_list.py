import requests
import pandas as pd
from datetime import datetime
import time
import os
import json
# import websocket
import threading
from queue import Queue
from requests.exceptions import RequestException, ProxyError
import random


def get_upbit_pairs():
    """获取Upbit所有USDT交易对"""
    try:
        url = "https://api.upbit.com/v1/market/all"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        markets = response.json()

        # 只过滤USDT交易对
        usdt_pairs = []
        for market in markets:
            if market['market'].startswith('USDT-'):
                usdt_pairs.append({
                    'market': market['market'],
                    'korean_name': market['korean_name'],
                    'english_name': market['english_name']
                })

        return pd.DataFrame(usdt_pairs)
    except Exception as e:
        print(f"获取Upbit交易对时出错: {e}")
        return None


def save_to_csv():
    """保存交易对信息到CSV文件"""
    # 创建输出目录
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 获取并保存Upbit交易对
    print("\n正在获取Upbit交易对...")
    upbit_pairs = get_upbit_pairs()
    if upbit_pairs is not None:
        upbit_filename = f'{output_dir}/upbit_usdt_pairs_{timestamp}.csv'
        upbit_pairs.to_csv(upbit_filename, index=False)
        print(f"Upbit交易对已保存到: {upbit_filename}")
        print(f"Upbit_usdt交易对总数: {len(upbit_pairs)}")


if __name__ == "__main__":
    print("开始获取交易对信息...")
    save_to_csv()
    print("完成！")