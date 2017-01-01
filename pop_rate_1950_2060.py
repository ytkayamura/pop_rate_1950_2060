# -*- coding: utf-8 -*-
import xlrd
import pandas as pd
import re

# 年代別人口構成比の推移を作成する

# (2000年以前はこちらを使う）
# 日本の将来推計人口（平成１４年１月推計）
# 各歳人口データ
# http://www.ipss.go.jp/pp-newest/j/newest02/newest02.asp
# http://www.ipss.go.jp/pp-newest/j/newest02/p_age2.xls
XLS1 = 'p_age2.xls'

# (2010年以降はこちらを使う)
# 日本の将来推計人口（平成24年1月推計）
# 出生中位(死亡中位)推計 （2011～2060年）
# 表１－９ 　男女年齢各歳別人口
# http://www.ipss.go.jp/syoushika/tohkei/newest04/sh2401smm.html
XLS2 = '1-9.xls'

# 2000年以前の年齢別人口を取得
def popu(dic):
	book = xlrd.open_workbook(XLS1)
	sheet_1 = book.sheet_by_index(0)

	ages = [sheet_1.cell(row, 0).value for row in range(sheet_1.nrows) if row > 2]

	def sub_popu(dic, ages, base_col):
		# 年表記を取得
		s = sheet_1.cell(1, base_col).value
		year_s = re.match("\d*", s).group()

		# 男女年齢別1000人単位人口を取得
		df = pd.DataFrame()
		df['ages'] = ages
		df['mens'] = [sheet_1.cell(row, base_col).value for row in range(sheet_1.nrows) if row > 2]
		df['womens'] = [sheet_1.cell(row, base_col + 1).value for row in range(sheet_1.nrows) if row > 2]
		df['all'] = df['mens'] + df['womens']

		dic["total" + year_s] = df['all'].sum()
		dic["total_men" + year_s] = df['mens'].sum()
		dic["total_women" + year_s] = df['womens'].sum()

		# 1950年以降を対象。2010年以降は新しい方のデータを使う
		if 1950 <= int(year_s) and int(year_s) < 2010:
			dic[year_s] = df

	for col in range(sheet_1.ncols):
		if col % 2: sub_popu(dic, ages, col)

# 2010年以降の年齢別人口を取得
def popu2(dic, sh_idx):
	book = xlrd.open_workbook(XLS2)
	sheet = book.sheet_by_index(sh_idx)
	c = sheet.cell(1, 0).value
	year_s = re.match('.*\((\d*)\)年', c).group(1)

	base_col = 0
	start_row = 4
	end_row1 = 59
	end_row2 = 55
	ages = [sheet.cell(row, base_col).value for row in range(start_row, end_row1)]
	ages += [sheet.cell(row, base_col + 5).value for row in range(start_row, end_row2)]
	mens = [sheet.cell(row, base_col + 2).value for row in range(start_row, end_row1)]
	mens += [sheet.cell(row, base_col + 2 + 5).value for row in range(start_row, end_row2)]
	womens = [sheet.cell(row, base_col + 3).value for row in range(start_row, end_row1)]
	womens += [sheet.cell(row, base_col + 3 + 5).value for row in range(start_row, end_row2)]
	allpop = [sheet.cell(row, base_col + 1).value for row in range(start_row, end_row1)]
	allpop += [sheet.cell(row, base_col + 1 + 5).value for row in range(start_row, end_row2)]
	df = pd.DataFrame()
	df['ages'] = ages
	df['mens'] = mens
	df['womens'] = womens
	df['all'] = allpop

	dic[year_s] = df

	dic["total" + year_s] = sheet.cell(3, 1).value
	dic["total_men" + year_s] = sheet.cell(3, 2).value
	dic["total_women" + year_s] = sheet.cell(3, 3).value

# 年代別集計、整形
def proc(dic, year, res):
	df = dic[year]

	# "100〜"とかを数値に
	def to_i(e):
		if type(e) is str:
			return int(re.match('\d*', e).group())
		else:
			return e
	df['ages'] = df['ages'].apply(to_i)

	# 年代区分を設定
	def age_class1(age):
		if age < 20:
			return '0-19'
		elif age < 66:
			return '20-65'
		else:
			return '66-'

	# 年代区分。現役世代を40代までバージョン
	def age_class2(age):
		if age < 20:
			return '0-19'
		elif age < 50:
			return '20-49'
		else:
			return '50-'

	df['class1'] = df['ages'].apply(age_class1)
	df['class2'] = df['ages'].apply(age_class2)
	
	# 年代別集計
	# group by。reset_index()でSeriesからDataFrameに変換
	sum_class1 = df.groupby('class1')['all'].sum().reset_index()
	sum_class2 = df.groupby('class2')['all'].sum().reset_index()
	
	# 割合を算出
	sum_class1['total'] = dic['total' + year]
	sum_class2['total'] = dic['total' + year]
	sum_class1['rate'] = sum_class1['all'] / sum_class1['total']
	sum_class2['rate'] = sum_class2['all'] / sum_class2['total']

	# 年代別集計結果を結合
	sum_20_49 = sum_class2[sum_class2['class2'] == '20-49'].copy()
	sum_class1.rename(columns={'class1': 'class'}, inplace=True)  # カラム名をclassに統一
	sum_20_49.rename(columns={'class2': 'class'}, inplace=True)   # カラム名をclassに統一
	ret = sum_class1.append(sum_20_49)
	ret = ret.sort_values(by='class')  # 年代順に並び替え
	ret = ret.reset_index(drop=True)  # インデクスを再設定

	# 各年の集計結果を結合
	if res.empty:
		res['class'] = ret['class']
	res[year] = ret['rate']

#####
# ここから処理開始
# Excelファイルよりデータを取得
dic = {}
popu(dic)  # 2000年以前
for sheet_i in [0, 7, 10, 20, 30, 40, 50]:  # 2010年から10年刻み＋2017年のシートから取得
	popu2(dic, sheet_i)  # 2010年以降

# データを取得した年を確認
keys = list(dic.keys())
years = list(filter(lambda s: s.isdigit(), keys))
years.sort()
print(years)

# 集計・整形実行
res = pd.DataFrame()
for y in years:
	proc(dic, y, res)
print(res)

# CSV出力
res.to_csv('pop_rate_1950_2060.csv')

