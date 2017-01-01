# pop_rate_1950_2060
国立社会保障・人口問題研究所の日本の将来推計人口データ(2010年以前は国勢調査実績データ)より、1950年から2060年の年代別人口構成比を集計し、CSV出力します。
## Sources
- p_ages2.xls
 - 日本の将来推計人口（平成１４年１月推計）
 - 各歳人口データ
 - http://www.ipss.go.jp/pp-newest/j/newest02/newest02.asp
 - http://www.ipss.go.jp/pp-newest/j/newest02/p_age2.xls
- 1-9.xls
 - 日本の将来推計人口（平成24年1月推計）
 - 出生中位(死亡中位)推計 （2011～2060年）
 - 表１－９ 　男女年齢各歳別人口
 - http://www.ipss.go.jp/syoushika/tohkei/newest04/sh2401smm.html

## Usage
    $ python pop_rate_1950_2060.py

## Dependencies
- pandas
- xlrd
