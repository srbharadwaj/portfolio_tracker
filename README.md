# Mutual fund portfolio Tracker

A simple DIY mutual fund tracker written in python.
For more info, please check the post https://duddukaasu.wordpress.com/2020/08/04/how-do-you-track-your-portfolio/

**How to use**
-
1) Download the package
2) Execute `pip install -r requirements.txt`
3) Execute `python3 myPortfolioScript.py transactions.csv` 

Once you execute the above under the `mfl_tmp` directory you will see a folder `sch` you will see induvidual schemes progress on a daily basis, open the csv in an excel file and plot for more details.
Also after the run you will see these files
`EmergencyPortFolioProgress.csv` - transactions which are tagged under goal emergency

`RetirementEquityPortFolioProgress.csv` - transactions which are tagged under goal retirement

`ChildEducationEquityPortFolioProgress.csv` - transactions which are tagged under goal child education

`OverallEquityPortFolioProgress.csv` - transactions which are tagged equity

`OverallDebtPortFolioProgress.csv` - transactions which are tagged debt

`OverallEntirePortFolioProgress.csv` - transactions which are tagged equity and debt, this is the entire portfolio

Currently only goals 'Emergency' , 'Retirement' , 'ChildEducation' are supported

**How should the `transactions.csv` file look like**
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

Please make sure that the column header has same names as shown above.


Scheme codes can be got from http://portal.amfiindia.com/spages/NAVopen.txt

Please mail me at srbharadwaj at gmail dot com for any issues. 

