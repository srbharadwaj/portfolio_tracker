# Mutual fund portfolio Tracker

A simple DIY mutual fund tracker written in python

**How to use**
-
1) Download the package
2) Execute `pip install -r requirements.txt`
3) Execute `python3 myPortfolioScript.py transactions.csv` 

**How should the transactions.csv file look like**
-

| Date  | Scheme Code | Scheme Name  | Type | Price  | Units | Amount  | Equity/Debt | Goal |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |------------- |

Example:

| Date  | Scheme Code | Scheme Name  | Type | Price  | Units | Amount  | Equity/Debt | Goal |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |------------- |
| 08-Jun-12| 101762| HDFC Equity Fund - Growth Option| Buy| 248.692| 4.021| 1000| Equity| Retirement
| 08-Jun-12| 101922| Canara Robeco Equity Diversified Fund - Regular Plan - Growth| Buy| 53.73| 18.612| 1000| Equity| ChildEducation
| 11-Jun-12| 101762| HDFC Equity Fund - Growth Option| Buy| 247.975| 8.065| 2000| Equity| Retirement
| 11-Jun-12| 101922| Canara Robeco Equity Diversified Fund - Regular Plan - Growth| Buy| 53.69| 37.251| 2000| Equity| ChildEducation
| 12-Jun-12| 108466| ICICI Prudential Bluechip Fund - Growth| Buy| 15.75| 126.984| 2000| Equity| Retirement
| 12-Jun-12| 102000| HDFC Top 100 Fund - Growth Option| Buy| 193.745| 10.323| 2000| Equity| Retirement

Please make sure that the column header has same names
Scheme code can be got from http://portal.amfiindia.com/spages/NAVopen.txt

Please mail me at srbharadwaj at gmail dot com for any issues. 

