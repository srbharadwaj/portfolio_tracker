import errno
from datetime import datetime
import requests
import re
import csv
import os
import logging
from .mflconst import *

log = logging.getLogger(__name__)
from multiprocessing.pool import ThreadPool as Pool
from collections import OrderedDict


class _eachSchemeInfo(object):
    def __init__(self, schcode, schname):
        log.debug("Inside _eachSchemeInfo init")
        self.schcode = schcode
        self.schname = schname
        self.dateNav = OrderedDict()

    def addDateNav(self, datestring, nav):
        self.dateNav[datestring] = nav

    def printDateNav(self):
        print
        self.dateNav

    def getDateNav(self):
        return self.dateNav


class _eachAMCsAllSchemeInfo(object):
    def __init__(self, amccode, amcname):
        log.debug("Inside _eachAMCsAllSchemeInfo init")
        self.amccode = amccode
        self.amcname = amcname
        self.schcodesandnames = {}
        self.schobjects = {}

    def addSchCodeAndName(self, schcode, schname, nav, datestring):
        self.schcodesandnames[schcode] = schname
        if schcode in self.schobjects.keys():
            self.schobjects[schcode].addDateNav(datestring, nav)
        else:
            o = _eachSchemeInfo(schcode, schname)
            self.schobjects[schcode] = o
            o.addDateNav(datestring, nav)

    def getAMCCode(self):
        return self.amccode

    def getAMCName(self):
        return self.amcname

    def getAMCCodeAndName(self):
        return [self.getAMCCode(), self.getAMCName()]

    def isSchemePresent(self, schcode):
        return schcode in self.schcodesandnames.keys()

    def getSchCodeAndName(self):
        return self.schcodesandnames

    def printAllSchDetails(self, schcode=''):
        if schcode == '':
            for schcode, schobj in self.schobjects.keys():
                print
                schcode
                print
                self.schcodesandnames[schcode]
                print
                schobj.printDateNav()
        else:
            o = self.schobjects[schcode]
            print
            schcode
            print
            self.schcodesandnames[schcode]
            print
            o.printDateNav()

    def getSchDetails(self, schcode):
        o = self.schobjects[schcode]
        return o.getDateNav()


class MFDatabaseClass(object):
    def __init__(self, getallschdata=False, getHistoricNav=False, getamc=None, getsch=None):
        log.debug("Inside MFDatabaseClass init")
        self.__indexPositions = {}
        self.__startdate = START_DATE
        self.__today = datetime.today().strftime(DDMMMYYYY_FORMAT)
        self.__allData = {}

        if not os.path.exists(os.path.dirname(MFDB_FILENAME)):
            try:
                os.makedirs(os.path.dirname(MFDB_FILENAME))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        if os.path.exists(MFDB_FILENAME):
            log.info("Reading data from  " + MFDB_FILENAME)
            with open(MFDB_FILENAME, 'r') as f:
                r = csv.reader(f)
                for row in r:
                    log.debug(row)
                    self.__processEachRowData(row)

        if getallschdata:
            self.getAndUpdateAllSchemeData(getHistoricNav, getamc, getsch)

    def printAMCSchData(self, amc='', sch=''):
        if amc == '':
            for amccode, eachobj in self.__allData.items():
                eachobj.printAllSchDetails(sch)
        else:
            self.__allData[amc].printAllSchDetails(sch)

    def getAMCSchData(self, amc=None, sch=None):
        if amc == None or sch == None:
            return self.__allData
        return self.__allData[amc].getSchDetails(sch)

    def getAMCSchCodeAndNames(self, amccode):
        return self.__allData[amccode].getSchCodeAndName()

    def getAndUpdateAllSchemeData(self, getforAmc=None, getforSch=None, getHistoricNav=False, getamc=None, getsch=None):
        pool = Pool(MAX_AMC_CODE_RANGE)
        for i in range(0, MAX_AMC_CODE_RANGE):
            pool.apply_async(self.__worker, (i, getforAmc, getforSch, getHistoricNav, getamc, getsch,))
        pool.close()
        pool.join()

        log.info("Number of AMC's are : " + str(len(self.__allData)))
        if getforAmc is None and getforSch is None:
            with open(MFDB_FILENAME, mode='w') as f:
                log.info("Writing all the scheme info data to csv file")
                w = csv.writer(f)
                for amccode, eachobj in self.__allData.items():
                    log.debug("AMC Code:" + amccode + " AMC name :" + eachobj.getAMCName())
                    schcodeandname = eachobj.getSchCodeAndName()
                    for code, name in schcodeandname.items():
                        log.debug("Schcode: " + code + " Sch Name: " + name)
                        w.writerow([amccode, eachobj.getAMCName(), code, name])
        else:
            log.info("Not writing all the scheme info data to csv file for now")

    def getAMCCodeForScheme(self, schcode):
        log.debug("Inside getAMCCodeForScheme")
        for amccode, eachobj in self.__allData.items():
            schcodeandname = eachobj.getSchCodeAndName()
            for code, name in schcodeandname.items():
                if code == schcode:
                    log.debug(amccode)
                    return amccode
        self.getAndUpdateAllSchemeData()
        for amccode, eachobj in self.__allData.items():
            schcodeandname = eachobj.getSchCodeAndName()
            for code, name in schcodeandname.items():
                if code == schcode:
                    log.info(amccode)
                    return amccode
        log.error("Could not get AMC code for the schcode: " + schcode)
        exit()

    def __worker(self, i, getforAmc, getforSch, getHistoricNav, getamc, getsch):
        schcodes = []
        amccode = str(i)
        if ((getforAmc is not None) and (getforAmc != amccode)):
            return

        log.info("Trying to find if there is an AMC with the code " + amccode)
        fullurl = NAV_HISTORY_URL.format(amccode, self.__startdate, self.__today)
        log.info(fullurl)
        r = requests.get(fullurl)
        if r.status_code != 200:
            log.error(ERROR2_TEXT)
            exit()
        if 'text/plain' in r.headers.get('content-type'):
            amcname = re.findall(r".*Mutual Fund.*", r.text)[0].encode('ascii', 'ignore').strip('\r')
            log.info("There is an AMC with the code " + amccode + " name is " + amcname)
            pat = ".*;.*"
            foundheader = 0
            intrestedlines = re.findall(pat, r.text)
            for eachline in intrestedlines:
                line = eachline.encode('ascii', 'ignore').strip('\r')
                if foundheader != 4:
                    for i in [SCHCODE_STRING, SCHNAME_STRING, NAV_STRING, DATE_STRING]:
                        if i in line:
                            indexpos = line.split(";").index(i)
                            self.__indexPositions[i] = indexpos
                            foundheader = foundheader + 1
                else:
                    schc = line.split(";")[self.__indexPositions[SCHCODE_STRING]]
                    schn = line.split(";")[self.__indexPositions[SCHNAME_STRING]]
                    nav = line.split(";")[self.__indexPositions[NAV_STRING]]
                    datestring = line.split(";")[self.__indexPositions[DATE_STRING]]
                    if ((getforSch is not None) and (getforSch != schc)):
                        continue
                    if schc not in schcodes:
                        schcodes.append(schc)
                    if getHistoricNav:
                        if ((getamc is not None) and (getsch is not None)):
                            if ((getamc == amccode) and (getsch == schc)):
                                self.__processEachRowData([amccode, amcname, schc, schn], [nav, datestring])
                        else:
                            self.__processEachRowData([amccode, amcname, schc, schn], [nav, datestring])

            log.info("Finished processing for AMC with the code " + amccode + " name is " + amcname)
        else:
            log.info("There is no AMC with the code " + amccode)

    def __processEachRowData(self, row, datenav=['', '']):
        amcc = row[0]
        amcn = row[1]
        schc = row[2]
        schn = row[3]
        nav = datenav[0]
        datestring = datenav[1]
        if amcc in self.__allData.keys():
            amcobj = self.__allData[amcc]
        else:
            amcobj = _eachAMCsAllSchemeInfo(amcc, amcn)
            self.__allData[amcc] = amcobj
        amcobj.addSchCodeAndName(schc, schn, nav, datestring)
