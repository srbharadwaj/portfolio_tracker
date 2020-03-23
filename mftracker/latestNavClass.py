import requests
import re
import logging
from .mflconst import *

log = logging.getLogger(__name__)


class LatestNavClass(object):
    def __init__(self, url=DEFAULT_NAV_URL):
        log.info("Getting the latest NAV..")
        self.__navdetails = {}
        self.__indexPositions = {}
        r = requests.get(url)
        if r.status_code != 200:
            log.debug(ERROR0_TEXT)
            exit()

        if 'text/plain' in r.headers.get('content-type'):
            pat = ".*;.*"
            foundheader = 0
            intrestedlines = re.findall(pat, r.text)
            for eachline in intrestedlines:
                #line = eachline.encode('ascii', 'ignore').strip('\r')
                line = eachline.strip('\r')
                if foundheader != 4:
                    for i in [SCHCODE_STRING, SCHNAME_STRING, NAV_STRING, DATE_STRING]:
                        if i in line:
                            #print(line.split(";"))
                            indexpos = line.split(";").index(i)
                            self.__indexPositions[i] = indexpos
                            foundheader = foundheader + 1
                else:
                    schc = line.split(";")[self.__indexPositions[SCHCODE_STRING]]
                    schn = line.split(";")[self.__indexPositions[SCHNAME_STRING]]
                    nav = line.split(";")[self.__indexPositions[NAV_STRING]]
                    navdate = line.split(";")[self.__indexPositions[DATE_STRING]]
                    self.__navdetails[schc] = [schn, nav, navdate]
        else:
            log.debug(ERROR1_TEXT)
            exit()

    def getNav(self, schcode):
        return self.__navdetails[str(schcode)][1]

    def getNavAndDate(self, schcode):
        return self.__navdetails[str(schcode)][1], self.__navdetails[str(schcode)][2]

    def getSchNameNavAndDate(self, schcode):
        return self.__navdetails[str(schcode)][0], self.__navdetails[str(schcode)][1], self.__navdetails[str(schcode)][
            2]
