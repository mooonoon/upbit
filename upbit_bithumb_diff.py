# 代码执行环境已重置，重新加载文件后继续处理
import pandas as pd

# 重新读取两个文件
upbit_krw = pd.read_csv(r'D:\ana\arbitrage\upbit_bithumb\output\upbit_krw_pairs_20250430_150954.csv')
bithumb_krw = pd.read_csv(r'D:\ana\arbitrage\upbit_bithumb\output\bithumb_krw_pairs_20250430_150450.csv')

# 提取币种名称
upbit_krw['coin'] = upbit_krw['market'].str.replace('KRW-', '', regex=False)
bithumb_krw['coin'] = bithumb_krw['market'].str.replace('KRW-', '', regex=False)

# 设置索引为 coin
upbit_info = upbit_krw.set_index('coin')[['korean_name', 'english_name']]
bithumb_info = bithumb_krw.set_index('coin')[['korean_name', 'english_name']]

# 找出交易对分类
common_coins = set(upbit_info.index).intersection(bithumb_info.index)
only_upbit = set(upbit_info.index) - set(bithumb_info.index)
only_bithumb = set(bithumb_info.index) - set(upbit_info.index)

# 构建详细信息 DataFrame
common_df = upbit_info.loc[list(common_coins)].reset_index()
only_upbit_df = upbit_info.loc[list(only_upbit)].reset_index()
only_bithumb_df = bithumb_info.loc[list(only_bithumb)].reset_index()

# 写入 Excel 文件
output_path = r'D:\ana\arbitrage\upbit_bithumb\output\upbit_bithumb_krw_comparison.xlsx'
with pd.ExcelWriter(output_path) as writer:
    common_df.to_excel(writer, sheet_name='Both_Exchanges', index=False)
    only_upbit_df.to_excel(writer, sheet_name='Only_Upbit', index=False)
    only_bithumb_df.to_excel(writer, sheet_name='Only_Bithumb', index=False)

output_path
