from portfolio_tracker.mftracker.latestNavClass import LatestNavClass
from portfolio_tracker.mftracker.mfDatabaseClass import MFDatabaseClass
from portfolio_tracker.mftracker.parseTransactionsClass import parseTransactionsClass
from portfolio_tracker.mftracker.portfolioUtils import *
import argparse
import logging.config


def main():
    logFormatter = logging.Formatter("%(asctime)s [%(module)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(level=logging.DEBUG)

    fileHandler = logging.FileHandler("mfl.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(level=logging.DEBUG)


    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(level=logging.INFO)
    consoleHandler.setFormatter(logFormatter)

    rootLogger.addHandler(fileHandler)
    rootLogger.addHandler(consoleHandler)
    import sys;
    rootLogger.info('Python %s on %s' % (sys.version, sys.platform))
    rootLogger.info("Starting...")

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="csv file containing transactions")
    args = parser.parse_args()
    rootLogger.info("File name passed is " + args.filename)

    ln = LatestNavClass()
    mfdb = MFDatabaseClass()

    pt = parseTransactionsClass(args.filename, mfdb)
    calculateEntirePortfolioProgress_Eq_De(pt)


if __name__ == '__main__':
    main()
