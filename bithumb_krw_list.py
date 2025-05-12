import requests
import pandas as pd
from datetime import datetime
import os


def get_bithumb_krw_pairs():
    """获取Bithumb所有KRW交易对"""
    try:
        url = "https://api.bithumb.com/public/ticker/ALL_KRW"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 提取交易对信息
        krw_pairs = []
        for currency in data['data']:
            if currency == 'date':  # 跳过日期字段
                continue
            krw_pairs.append({
                'market': f'KRW-{currency}',
                'currency': currency,
                'korean_name': '',  # Bithumb API不提供韩文名称
                'english_name': ''  # Bithumb API不提供英文名称
            })

        return pd.DataFrame(krw_pairs)
    except Exception as e:
        print(f"获取Bithumb交易对时出错: {e}")
        return None


def save_to_csv():
    """保存交易对信息到CSV文件"""
    # 创建输出目录
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 获取并保存Bithumb交易对
    print("\n正在获取Bithumb交易对...")
    bithumb_pairs = get_bithumb_krw_pairs()
    if bithumb_pairs is not None:
        filename = f'{output_dir}/bithumb_krw_pairs_{timestamp}.csv'
        bithumb_pairs.to_csv(filename, index=False)
        print(f"Bithumb交易对已保存到: {filename}")
        print(f"Bithumb韩元交易对总数: {len(bithumb_pairs)}")


if __name__ == "__main__":
    print("开始获取Bithumb交易对信息...")
    save_to_csv()
    print("完成！")