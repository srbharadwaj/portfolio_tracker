from importlib import reload

from .mflconst import *
import requests
import csv
import re
import io
import os
import errno
from dateutil.parser import parse
from re import sub
from datetime import datetime, timedelta, date
from multiprocessing.pool import ThreadPool as Pool
from collections import OrderedDict
import logging

log = logging.getLogger(__name__)


class _eachMFTransactionsData(object):
    def __init__(self, eachd, mfdb):
        self.mfdb = mfdb
        self.listOfTransactions = []  # date,type,price,units,amount
        self.listOfCumulativeData = []  # date,tunits,tamount
        self.ordTrans = OrderedDict()  # date: type:price:units:amount
        self.cumulativeOrdTrans = OrderedDict()  # "Date":"Type","Price","Units","Amount","Total Units","Total Amount","Total Value"
        self.cumulativeAllDatesData = OrderedDict()  # "Date": "NAV","Total Units","Total Amount","Total Value"
        self.sortuniqdates = []
        self.datenav = OrderedDict()  # date: nav
        self.latestTaAndTv = [0, 0]  # tu,tv
        self.goal = None
        self.add(eachd)

    def getListOfOrdTrans(self, tilld):
        retOrderTrans = OrderedDict()
        for d, v in self.ordTrans.items():
            tilld_obj = datetime.strptime(tilld, DDMMMYYYY_FORMAT)
            # print d,tilld_obj
            if d < tilld_obj:
                retOrderTrans[d] = v
            elif d == tilld_obj:
                retOrderTrans[d] = v
                break
            else:
                break
        return retOrderTrans

    def resetLatestTaAndTv(self):
        self.latestTaAndTv = [0, 0]  # tu,tv

    def getLatestTaAndTv(self, d):
        # latestTaAndTv = [0, 0]
        if d.strftime(DDMMMYYYY_FORMAT) in self.cumulativeAllDatesData.keys():
            val = self.cumulativeAllDatesData[d.strftime(DDMMMYYYY_FORMAT)]
            ta = val[2]
            tv = val[3]
            self.latestTaAndTv = [ta, tv]
        return self.latestTaAndTv

    def processTransactions(self):
        self.calculateIfFundClosed()
        self.getFirstAndLastDate()
        self.mfcode = self.mfdb.getAMCCodeForScheme(self.schcode)

    def getTotalAmt1(self, TSU, buyList):
        ta = 0
        for s in buyList:
            d = s[0]
            t = s[1].strip()
            p = s[2]
            bu = s[3]
            a = s[4]
            if TSU <= bu:
                ta = ta + (TSU * p)
                return ta
            else:
                ta = ta + (bu * p)
                TSU = TSU - bu
            if TSU <= 1:
                return ta

    def getTotalAmt(self, TSU, buyList):
        ta = 0
        for s in buyList:
            d = s[0]
            t = s[1].strip()
            p = s[2]
            bu = s[3]
            a = s[4]

            if TSU > bu:
                TSU = TSU - bu
                ta = max(0,(round((ta + a), 4)))
            elif TSU <= bu:
                ta = max(0,(round((ta + (TSU * p)), 4)))
                break
            # if self.schcode == '102000':
            #    print bu,TSU,ta,p
        # if self.schcode == '102000':
        #    print bu, TSU, ta,p
        return ta

    def getCumulativeTransactionData(self):
        buyList = []
        sellList = []
        for d, key in self.ordTrans.items():
            t = key[0]
            p = key[1]
            u = key[2]
            a = key[3]
            if t.lower() == "Buy".lower():
                buyList.append([d, t, p, u, a])
            else:
                sellList.append([d, t, p, u, a])
        sTotalList = OrderedDict()
        TSU = 0
        for s in sellList:
            d = s[0]
            t = s[1].strip()
            p = s[2]
            u = s[3]
            a = s[4]
            TSU = TSU + u
            ta = self.getTotalAmt(TSU, buyList)
            sTotalList[d] = ta
            # try:
            #    pv = sTotalList.values()[-1]
            #    ta = ta - pv
            #    sTotalList[d] = ta
            # except IndexError:
            #    sTotalList[d] = ta
        newsTotalList = OrderedDict()
        for k, v in sTotalList.items():
            i = list(sTotalList.keys()).index(k)
            if i != 0:
                sumv = list(sTotalList.values())[i - 1]
            else:
                sumv = 0
            retval = v - sumv
            newsTotalList[k] = retval

        tu = 0
        ta = 0
        for d, key in self.ordTrans.items():
            t = key[0]
            p = key[1]
            u = key[2]
            a = key[3]
            if t.lower() == "Buy".lower():
                tu = tu + u
                ta = ta + a
            else:
                tu = max(0,(tu - u))
                ta = max(0,(ta - newsTotalList[d]))
            self.cumulativeOrdTrans[d] = [t, p, u, a, round(tu, 4), round(ta, 4), max(0,(round((tu * p), 4)))]

    def getCumulativeAllDatesData(self):
        row = None
        for d, n in self.datenav.items():
            dobj = parse(d)
            if dobj in self.cumulativeOrdTrans.keys():
                row = self.cumulativeOrdTrans[dobj]
                t = row[0]
                p = row[1]
                u = row[2]
                a = row[3]
                tu = row[4]
                ta = row[5]
                tv = row[6]
                self.cumulativeAllDatesData[d] = [n, tu, ta, tv]
            else:
                if row is None:
                    self.cumulativeAllDatesData[d] = [n, 0, 0, 0]
                else:
                    t = row[0]
                    p = row[1]
                    u = row[2]
                    a = row[3]
                    tu = row[4]
                    ta = row[5]
                    tv = row[6]
                    self.cumulativeAllDatesData[d] = [n, tu, ta, max(0,(round((tu * float(n)), 4)))]
        self.calculateXIRR()

    def calculateXIRR(self):
        log.info("Calculating XIRR...")
        # print(self.cumulativeOrdTrans)
        for d, val in self.cumulativeAllDatesData.items():
            tv = val[3]
            cashflows = []
            for eachd, v in self.cumulativeOrdTrans.items():
                dobj = parse(d)
                eachdobj = eachd
                if eachdobj <= dobj:
                    t = v[0]
                    amt = v[3]
                    if t.lower() == 'Buy'.lower():
                        cashflows.append((eachdobj.date(), -amt))
                    else:
                        cashflows.append((eachdobj.date(), amt))
            cashflows.append((dobj.date(), tv))
            # print cashflows
            cashflowsorted = sorted(cashflows, key=lambda x: x[0])
            xirrval = xirr(cashflowsorted)
            # print d, xirrval
            xirrval_str = "{:.2%}".format(xirrval)
            self.cumulativeAllDatesData[d] = val + [xirrval_str]

    def getAmtToDeduct(self, sTotalList, d):
        out = 0
        for dd, v in sTotalList.items():
            if dd == d:
                out = out + v
                break
            else:
                out = out - v
        return out

    def writeCumulativeToFile(self):
        log.debug("Inside writeCumulativeToFile")
        fname = SCH_PATH + format_filename(self.schname + self.schcode) + ".csv"
        if not os.path.exists(os.path.dirname(SCH_PATH)):
            try:
                os.makedirs(os.path.dirname(SCH_PATH))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        if self.cumulativeAllDatesData:
            with open(fname, mode='w') as f:
                log.info("Writing all the sch info data to csv file " + self.schname)
                w = csv.writer(f)
                # w.writerow(["Date","Type","Price","Units","Amount","Total Units","Total Amount","Total Value"])
                # for d, key in self.cumulativeOrdTrans.items():
                #    w.writerow([d.strftime(DDMMMYYYY_FORMAT)]+key)
                w.writerow(["Date", "NAV", "Total Units", "Total Amount", "Total Value", "XIRR"])
                for d, key in self.cumulativeAllDatesData.items():
                    w.writerow([d] + key)

    def getNAVFomFirstToLastDates(self):
        self.navfilename = NAV_PATH + format_filename(self.schname + self.schcode) + ".csv"
        if not os.path.exists(os.path.dirname(NAV_PATH)):
            try:
                os.makedirs(os.path.dirname(NAV_PATH))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        # If NAV csv is present
        # Read from csv
        if os.path.exists(self.navfilename):
            log.info("Reading data from  " + self.navfilename)
            with open(self.navfilename, 'r') as f:
                r = csv.reader(f)
                self.datenav = OrderedDict(r)
            alldates = self.datenav.keys()
            datetimelist = []
            for ed in alldates:
                datetimelist.append(parse(ed))
            fd = min(datetimelist)
            ld = max(datetimelist)
            getd = False
            if fd != self.firstTransactionDate:
                f = self.firstTransactionDate
                l = self.lastDate
                getd = True
            if ld != self.lastDate:
                f = max(datetimelist)
                l = self.lastDate
                getd = True
            if fd != self.firstTransactionDate and ld != self.lastDate:
                f = self.firstTransactionDate
                l = self.lastDate
            if getd:
                self.getHistoricNavFromAmfi(f, l)
        else:
            self.getHistoricNavFromAmfi(self.firstTransactionDate, self.lastDate)

        if self.datenav:
            with open(self.navfilename, mode='w') as f:
                log.info("Writing all the nav info data to csv file " + self.schname)
                w = csv.writer(f)
                for d, n in self.datenav.items():
                    w.writerow([d, n])

    def getHistoricNavFromAmfi(self, fd, ld):
        # Check the dates
        self.__indexPositions = {}
        log.info("Trying to get nav details from amfi for scheme " + self.schname + " " + self.schcode)
        url = NAV_HISTORY_URL.format(self.mfcode, fd.strftime(DDMMMYYYY_FORMAT), ld.strftime(DDMMMYYYY_FORMAT))
        log.info(url)
        r = requests.get(url)
        if r.status_code != 200:
            log.error(ERROR2_TEXT)
            exit()
        if 'text/plain' in r.headers.get('content-type'):
            patschcode = ".*" + self.schcode + ";.*"
            pat = ".*;.*"
            foundheader = 0
            intrestedlines = re.findall(pat, r.text)
            for eachline in intrestedlines:
                #line = eachline.encode('ascii', 'ignore').strip('\r')
                line = eachline.strip('\r')
                if foundheader != 4:
                    for i in [SCHCODE_STRING, SCHNAME_STRING, NAV_STRING, DATE_STRING]:
                        if i in line:
                            indexpos = line.split(";").index(i)
                            self.__indexPositions[i] = indexpos
                            foundheader = foundheader + 1
                else:
                    break
            if foundheader == 4:
                intrestedlines = re.findall(patschcode, r.text)
                for eachline in intrestedlines:
                    #line = eachline.encode('ascii', 'ignore').strip('\r')
                    line = eachline.strip('\r')
                    d = line.split(";")[self.__indexPositions[DATE_STRING]]
                    n = line.split(";")[self.__indexPositions[NAV_STRING]]
                    self.datenav[d] = n
        log.info("Done getting nav details from amfi for scheme " + self.schname + " " + self.schcode)

    def prepareOrderedDictTransactions(self):
        log.debug("Inside prepareOrderedDictTransactions")
        datetimelist = []
        for lt in self.listOfTransactions:
            datetimelist.append(lt[0])
        self.sortuniqdates = list(set(datetimelist))
        self.sortuniqdates.sort()

        for eachdate in self.sortuniqdates:
            ltd = []
            for lt in self.listOfTransactions:
                d = lt[0]
                if d == eachdate:
                    ltd.append(lt)
            # log.info(ltd)
            if len(ltd) == 1:
                d = ltd[0][0]
                t = ltd[0][1]
                p = ltd[0][2]
                u = ltd[0][3]
                a = ltd[0][4]
                self.ordTrans[d] = [t, p, u, a]
            else:
                tu = 0
                ta = 0
                for eacht in ltd:
                    d = eacht[0]
                    t = eacht[1]
                    p = eacht[2]
                    u = eacht[3]
                    a = eacht[4]
                    if t.lower() == 'Buy'.lower():
                        tu = tu + float(u)
                        ta = ta + float(a)
                    else:
                        tu = tu - float(u)
                        ta = ta - float(a)
                if tu < 0:
                    t = 'Sell'
                else:
                    t = 'Buy'
                self.ordTrans[d] = [t, p, abs(tu), abs(ta)]

    def getFirstAndLastDate(self):
        datetimelist = []
        for lt in self.listOfTransactions:
            datetimelist.append(lt[0])
        self.firstTransactionDate = min(datetimelist)
        if self.fundClosed:
            self.lastDate = max(datetimelist)
        else:
            self.lastDate = datetime.today()

        # self.rangeOfActiveDates = []
        # delta = self.lastDate - self.firstTransactionDate  # timedelta
        # for i in range(delta.days + 1):
        #    self.rangeOfActiveDates.append(self.firstTransactionDate + timedelta(i))

    def calculateIfFundClosed(self):
        tunits = 0
        for lt in self.listOfTransactions:
            units = max(0,(round(lt[3], 4)))
            type = lt[1]
            if type.lower() == 'Buy'.lower():
                tunits = tunits + units
            else:
                tunits = tunits - units
        self.tunits = abs(round(tunits, 4))
        if tunits <= 0:
            self.fundClosed = True
        else:
            self.fundClosed = False

    def add(self, eachd):
        for k, v in eachd.items():
            # key = k.encode('utf-8').strip()
            # val = v.encode('utf-8').strip()
            key = k.strip()
            val = v.strip()

            if TRANS_SCHCODE_STRING in key:
                self.schcode = val
            if TRANS_SCHNAME_STRING in key:
                self.schname = val
            if TRANS_EORD in key:
                self.eod = val
            if TRANS_GOAL in key:
                self.goal = val
            if "Date" in key:
                d = val
                dat = parse(d)
            if TRANS_TYPE in key:
                type = val
            if TRANS_PRICE in key:
                p = val
                # print p
                price = float(sub(r'[^\d.]', '', p))
            if TRANS_UNITS in key:
                units = float(val)
            if TRANS_AMOUNT in key:
                a = val
                amt = float(sub(r'[^\d.]', '', a))
        self.listOfTransactions.append([dat, type, price, units, amt])

    def getlistOfTransactions(self):
        return self.listOfTransactions

    def getSchName(self):
        return self.schname

    def printDetails(self):
        print
        "MF/AMC Code: " + self.mfcode
        print
        "Scheme Code: " + self.schcode
        print
        "Scheme Name: " + self.getSchName()
        print
        "First Trans Date: " + str(self.firstTransactionDate)
        print
        "Last Date: " + str(self.lastDate)
        print
        "Fund Closed: " + str(self.fundClosed)
        print
        "Total Units: " + str(self.tunits)
        print
        "List of sortuniqdates: "
        print
        self.sortuniqdates
        print
        "List of transactions: "
        print
        self.getlistOfTransactions()
        print
        "List of ordered transactions: "
        print
        self.ordTrans
        print
        "List of cumulative ordered transactions: "
        print
        self.cumulativeOrdTrans
        print
        "List of cumulative all dates data: "
        print
        self.cumulativeAllDatesData
        print
        "List of date nav: "
        print
        self.datenav


class parseTransactionsClass(object):
    def __init__(self, filename, mfdb):
        import sys
        reload(sys)
        #sys.setdefaultencoding('utf-8')


        self.allMFTransactionsObjs = {}
        log.info("Reading from the file " + filename)
        reader = csv.DictReader(io.open(filename, 'r'))
        dict_list = []
        for line in reader:
            dict_list.append(line)
        log.debug("dict_list is..")
        log.debug(dict_list)
        # print dict_list
        for eachd in dict_list:
            for k, v in eachd.items():
                #key = k.encode('utf-8').strip()
                #val = v.encode('utf-8').strip()
                key = k.strip()
                val = v.strip()
                # print key,val

                if TRANS_SCHCODE_STRING in key:
                    if val in self.allMFTransactionsObjs.keys():
                        self.allMFTransactionsObjs[val].add(eachd)
                    else:
                        o = _eachMFTransactionsData(eachd, mfdb)
                        self.allMFTransactionsObjs[val] = o

        pool = Pool(len(self.allMFTransactionsObjs))
        for schcode, eachobj in self.allMFTransactionsObjs.items():
            pool.apply_async(self.__worker0, (eachobj,))
        pool.close()
        pool.join()

        '''
        pool = Pool(len(self.allMFTransactionsObjs))
        for schcode, eachobj in self.allMFTransactionsObjs.items():
            pool.apply_async(self.__worker1, (eachobj,))
        pool.close()
        pool.join()
        '''
        for schcode, eachobj in self.allMFTransactionsObjs.items():
            eachobj.processTransactions()
            eachobj.getNAVFomFirstToLastDates()
            eachobj.getCumulativeTransactionData()
            eachobj.getCumulativeAllDatesData()
            eachobj.writeCumulativeToFile()

    def __worker1(self, eachobj):
        eachobj.processTransactions()
        eachobj.getNAVFomFirstToLastDates()
        eachobj.getCumulativeTransactionData()
        eachobj.getCumulativeAllDatesData()
        eachobj.writeCumulativeToFile()

    def __worker0(self, eachobj):
        eachobj.prepareOrderedDictTransactions()
