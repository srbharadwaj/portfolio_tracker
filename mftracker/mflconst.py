import string

# Defaults do NOT change it
VERSION = 1.0

DEFAULT_NAV_URL = "http://portal.amfiindia.com/spages/NAVopen.txt"
# http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=26&tp=1&frmdt=03-Sep-2002&todt=05-Sep-2018
NAV_HISTORY_URL = "http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf={0}&tp=1&frmdt={1}&todt={2}"
# https://www.nseindia.com/products/dynaContent/equities/indices/total_returnindices.jsp?indexType=NIFTY%20NEXT%2050&fromDate=28-12-2015&toDate=10-2-2016
INDEX_URL = "https://www1.nseindia.com/products/dynaContent/equities/indices/total_returnindices.jsp?indexType={0}&fromDate={1}&toDate={2}"

MFDB_FILENAME = "mfl_tmp/mfdb.csv"  # AMCCODE,AMCNAME,SCHCODE,SCHNAME
NAV_PATH = "mfl_tmp/nav/"
SCH_PATH = "mfl_tmp/sch/"
INDEX_PATH = "mfl_tmp/index/"
SCHDETAILS_PATH = "schdetails/"
TRANS_DATE_STRING = "Date"
TRANS_SCHCODE_STRING = "Scheme Code"
TRANS_SCHNAME_STRING = "Scheme Name"
TRANS_UNITS = "Units"
TRANS_AMOUNT = "Amount"
TRANS_EORD = "Equity/Debt"
TRANS_TYPE = "Type"
TRANS_PRICE = "Price"
TRANS_GOAL = "Goal"

SCHCODE_STRING = "Scheme Code"
SCHNAME_STRING = "Scheme Name"
NAV_STRING = "Net Asset Value"
DATE_STRING = "Date"
ERROR0_TEXT = "ERROR:1: Unable to get NAV data, status code is not 200, please contact Suhas (srbharadwaj@gmail.com)"
ERROR1_TEXT = "ERROR:0: Unable to get NAV data, please contact Suhas (srbharadwaj@gmail.com)"
ERROR2_TEXT = "ERROR:1: Unable to get NAV History data, status code is not 200, please contact Suhas (srbharadwaj@gmail.com)"
ERROR3_TEXT = "ERROR:0: Unable to get NAV History data, please contact Suhas (srbharadwaj@gmail.com)"
DDMMMYYYY_FORMAT = "%d-%b-%Y"
DDMMYYYY_FORMAT = "%d-%m-%Y"
MAX_AMC_CODE_RANGE = 100
START_DATE = "03-Apr-2006"
INDEX_START_DATE = "01-01-1989"

# Indexs
NIFTY50 = "NIFTY 50"
NIFTYNEXT50 = "NIFTY NEXT 50"
NIFTY100 = "NIFTY 100"
NIFTY200 = "NIFTY 200"
NIFTY500 = "NIFTY 500"
NIFTYMIDCAP150 = "NIFTY MIDCAP 150"
NIFTYMIDCAP50 = "NIFTY MIDCAP 50"
NIFTYMIDCAP100 = "NIFTY MIDCAP 100"
NIFTY100EW = "NIFTY100 EQUAL WEIGHT"
NIFTYLARGEMIDCAP250 = "NIFTY LARGEMIDCAP 250"
NIFTYMIDCAP150QUAITY50 = "NIFTY MIDCAP150 QUALITY 50"
NIFTYSMALLCAP250 = "NIFTY SMALLCAP 250"
NIFTY500VALUE50 = "NIFTY500 VALUE 50"

# LIST_OF_INDEXES = [NIFTY50,NIFTYNEXT50,NIFTY200,NIFTY100,NIFTY500,NIFTY100EW,NIFTYMIDCAP150,NIFTYMIDCAP50,NIFTYMIDCAP100,NIFTYLARGEMIDCAP250,NIFTYMIDCAP150QUAITY50]
LIST_OF_INDEXES = [NIFTY100, NIFTY50, NIFTYNEXT50, NIFTYMIDCAP150, NIFTYSMALLCAP250,NIFTY500VALUE50]


#BT CONSTANTS
AMT = 1000
NUMYEARS = 20
EQR = 12
DER = 7
REBALANCE = True
EQRATIO = None

'''
A single function that calculates IRR using Newton's Method
'''


def xirr(transactions):
    '''
    Calculates the Internal Rate of Return (IRR) for an irregular series of cash flows (XIRR)
    Takes a list of tuples [(date,cash-flow),(date,cash-flow),...]
    Returns a rate of return as a percentage
    '''

    years = [(ta[0] - transactions[0][0]).days / 365. for ta in transactions]

    all_less_than_a_year = True
    for eachy in years:
        if eachy >= 1:
            all_less_than_a_year = False
            break
    if all_less_than_a_year:
        return 0
    residual = 1.0
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, trans in enumerate(transactions):
            # print i,trans
            try:
                residual += trans[1] / pow(guess, years[i])
            except ZeroDivisionError:
                continue
            except ValueError:
                continue
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess - 1


# https://gist.github.com/seanh/93666
def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename
