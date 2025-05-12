import pandas as pd

# 读取上传的两个文件
krw_pairs = pd.read_csv('/mnt/data/upbit_krw_pairs_20250427_104457.csv')
usdt_pairs = pd.read_csv('/mnt/data/upbit_usdt_pairs_20250427_150837.csv')

# 查看前几行，了解数据结构
# krw_pairs.head(), usdt_pairs.head()

# 提取币种（去掉市场前缀 KRW- / USDT-）
krw_pairs['coin'] = krw_pairs['market'].str.replace('KRW-', '', regex=False)
usdt_pairs['coin'] = usdt_pairs['market'].str.replace('USDT-', '', regex=False)

# 找出相同的交易对（币种）
common_coins = set(krw_pairs['coin']).intersection(set(usdt_pairs['coin']))

# 只在KRW市场有的交易对
only_krw_coins = set(krw_pairs['coin']) - set(usdt_pairs['coin'])

# 只在USDT市场有的交易对
only_usdt_coins = set(usdt_pairs['coin']) - set(krw_pairs['coin'])

# common_coins, only_krw_coins, only_usdt_coins

# 整理数据，分别为三张表
common_coins_df = pd.DataFrame({'coin': list(common_coins)})
only_krw_coins_df = pd.DataFrame({'coin': list(only_krw_coins)})
only_usdt_coins_df = pd.DataFrame({'coin': list(only_usdt_coins)})

# 将三张表写入一个Excel文件，不同sheet
with pd.ExcelWriter('/mnt/data/upbit_market_pairs_comparison.xlsx') as writer:
    common_coins_df.to_excel(writer, sheet_name='Common_Pairs', index=False)
    only_krw_coins_df.to_excel(writer, sheet_name='Only_KRW_Pairs', index=False)
    only_usdt_coins_df.to_excel(writer, sheet_name='Only_USDT_Pairs', index=False)

'/mnt/data/upbit_market_pairs_comparison.xlsx'
