from dateutil.parser import parse
from .mflconst import *
from collections import OrderedDict
import csv

import logging

log = logging.getLogger(__name__)


def getAllXIRR(pt, finalOveralEverythinglDict, eod="All", goal=None):
    log.info("Get getAllXIRR for eod: " + eod + " Goal: " + str(goal) + " ....")
    finalout = {}
    for d, v in finalOveralEverythinglDict.items():
        alltrans = {}
        tv = v[1]
        for schcode, eachSchObj in pt.allMFTransactionsObjs.items():
            if goal is None:
                if eod == "All":
                    pass
                elif eachSchObj.eod.strip().lower() == eod.lower():
                    pass
                else:
                    continue
            else:
                if goal.lower() == eachSchObj.goal.strip().lower():
                    if eod == "All":
                        pass
                    elif eachSchObj.eod.strip().lower() == eod.lower():
                        pass
                    else:
                        continue
                else:
                    continue

            transOrd = eachSchObj.getListOfOrdTrans(tilld=d)
            if transOrd:
                for eachd, val in transOrd.items():
                    type = val[0]
                    amt = val[3]
                    if eachd in alltrans.keys():
                        a = alltrans[eachd]
                        if type.lower() == 'buy':
                            a = a - amt
                        else:
                            a = a + amt
                        alltrans[eachd] = a
                    else:
                        if type.lower() == 'buy':
                            alltrans[eachd] = -amt
                        else:
                            alltrans[eachd] = amt

        if parse(d) in alltrans.keys():
            a = alltrans[parse(d)]
            a = a + tv
            alltrans[parse(d)] = a
        else:
            alltrans[parse(d)] = tv
        cashflows = []
        for dobj, amt in alltrans.items():
            cashflows.append((dobj.date(), amt))
        # print cashflows
        cashflowsorted = sorted(cashflows, key=lambda x: x[0])
        xirrval = xirr(cashflowsorted)
        xirrval_str = "{:.2%}".format(xirrval)
        finalout[d] = xirrval_str
    # print finalout
    return finalout


def getFinalOverAllDict(pt, eod=None, goal=None):
    retDict = OrderedDict()

    overall_fd = []
    for schcode, eachSchObj in pt.allMFTransactionsObjs.items():
        for eachk in eachSchObj.cumulativeAllDatesData.keys():
            if goal is None:
                if eod is None:
                    d = parse(eachk)
                    overall_fd.append(d)
                elif eachSchObj.eod.lower() == eod.lower():
                    d = parse(eachk)
                    overall_fd.append(d)
                else:
                    continue
            else:
                if goal.lower() == eachSchObj.goal.lower():
                    if eod is None:
                        d = parse(eachk)
                        overall_fd.append(d)
                    elif eachSchObj.eod.lower() == eod.lower():
                        d = parse(eachk)
                        overall_fd.append(d)
                    else:
                        continue

    od = list(set(overall_fd))
    od.sort()

    for eachd in od:
        ta_all = 0
        tv_all = 0
        for schcode, eachSchObj in pt.allMFTransactionsObjs.items():
            if goal is None:
                if eod is None:
                    out = eachSchObj.getLatestTaAndTv(eachd)
                    ta_all = ta_all + out[0]
                    tv_all = tv_all + out[1]
                elif eachSchObj.eod.lower() == eod.lower():
                    out = eachSchObj.getLatestTaAndTv(eachd)
                    ta_all = ta_all + out[0]
                    tv_all = tv_all + out[1]
                    # print("Getting for " + eod)
                    # print(eachd,ta_all,tv_all)
                else:
                    continue
            else:
                if goal.lower() == eachSchObj.goal.lower():
                    if eod is None:
                        out = eachSchObj.getLatestTaAndTv(eachd)
                        ta_all = ta_all + out[0]
                        tv_all = tv_all + out[1]
                    elif eachSchObj.eod.lower() == eod.lower():
                        out = eachSchObj.getLatestTaAndTv(eachd)
                        ta_all = ta_all + out[0]
                        tv_all = tv_all + out[1]
                    else:
                        continue
                else:
                    continue
        if tv_all > 0:
            retDict[eachd.strftime(DDMMMYYYY_FORMAT)] = [ta_all, tv_all, tv_all - ta_all]
    for schcode, eachSchObj in pt.allMFTransactionsObjs.items():
        eachSchObj.resetLatestTaAndTv()
    return retDict


def calculateEntirePortfolioProgress_Eq_De(pt):
    log.info("Calculating OverallEntirePortFolioProgress...")

    # print od

    finalOveralEverythinglDict = getFinalOverAllDict(pt)
    finalOverallEquityDict = getFinalOverAllDict(pt, eod="Equity")
    finalOverallDebtDict = getFinalOverAllDict(pt, eod="Debt")

    overallxirr = getAllXIRR(pt, finalOveralEverythinglDict)
    with open("OverallEntirePortFolioProgress.csv", mode='w') as f:
        log.info("Writing OverallEntirePortFolioProgress...")
        w = csv.writer(f)
        w.writerow(["Date", "Total Amount", "Total Value", "Gains/Losses", "XIRR"])
        for d, v in finalOveralEverythinglDict.items():
            w.writerow([d] + v + [overallxirr[d]])

    eqxirr = getAllXIRR(pt, finalOverallEquityDict, eod="Equity")
    with open("OverallEquityPortFolioProgress.csv", mode='w') as f:
        log.info("Writing OverallEquityPortFolioProgress...")
        w = csv.writer(f)
        w.writerow(["Date", "Total Amount", "Total Value", "Gains/Losses", "XIRR"])
        for d, v in finalOverallEquityDict.items():
            w.writerow([d] + v + [eqxirr[d]])

    dexirr = getAllXIRR(pt, finalOverallDebtDict, eod="Debt")
    with open("OverallDebtPortFolioProgress.csv", mode='w') as f:
        log.info("Writing OverallDebtPortFolioProgress...")
        w = csv.writer(f)
        w.writerow(["Date", "Total Amount", "Total Value", "Gains/Losses", "XIRR"])
        for d, v in finalOverallDebtDict.items():
            w.writerow([d] + v + [dexirr[d]])

    # Goals
    GoalOverallEquityRetlDict = getFinalOverAllDict(pt, eod="Equity", goal="Retirement")
    GoalOverallEquityChildEdulDict = getFinalOverAllDict(pt, eod="Equity", goal="ChildEducation")
    GoalOverallEquityEmerDict = getFinalOverAllDict(pt, eod="Debt", goal="Emergency")

    goal_eqxirr = getAllXIRR(pt, GoalOverallEquityRetlDict, eod="Equity", goal="Retirement")
    with open("RetirementEquityPortFolioProgress.csv", mode='w') as f:
        log.info("Writing RetirementEquityPortFolioProgress...")
        w = csv.writer(f)
        w.writerow(["Date", "Total Amount", "Total Value", "Gains/Losses", "XIRR"])
        for d, v in GoalOverallEquityRetlDict.items():
            w.writerow([d] + v + [goal_eqxirr[d]])

    goal_eqxirr = getAllXIRR(pt, GoalOverallEquityChildEdulDict, eod="Equity", goal="ChildEducation")
    with open("ChildEducationEquityPortFolioProgress.csv", mode='w') as f:
        log.info("Writing ChildEducationEquityPortFolioProgress...")
        w = csv.writer(f)
        w.writerow(["Date", "Total Amount", "Total Value", "Gains/Losses", "XIRR"])
        for d, v in GoalOverallEquityChildEdulDict.items():
            w.writerow([d] + v + [goal_eqxirr[d]])

    goal_eqxirr = getAllXIRR(pt, GoalOverallEquityEmerDict, eod="Debt", goal="Emergency")
    with open("EmergencyPortFolioProgress.csv", mode='w') as f:
        log.info("Writing EmergencyPortFolioProgress...")
        w = csv.writer(f)
        w.writerow(["Date", "Total Amount", "Total Value", "Gains/Losses", "XIRR"])
        for d, v in GoalOverallEquityEmerDict.items():
            w.writerow([d] + v + [goal_eqxirr[d]])