__author__ = 'sergeygolubev'

#import modules
import csv
import itertools
from datetime import datetime
import copy
import operator
import timer
import time
from timer import timer

class VCAnalysis:

    def __init__(self, filename, startdate=1990, enddate=2013):

        #initilize file with data
        self.csvfile = open(filename,'rU')

        #list with dates always on one greater cause Python syntax
        self.dates = [i for i in range (startdate,enddate)]
        print 'Target dates: ' + str(self.dates)

        self.data = []
        self.dataCleanCompany = []
        #create a dictionary of years as first key with included dictionaries for VC name as second key and company name as a value
        self.dataDic = {}
        #and a dictionary for cleantechs' VCs
        self.dataDicCleanVC = {}

        #temprory dictionaries for given dates
        self.tempDictTargetDate = {}
        self.tempDictTargetFocalDate = {}

        #temprory dictionary for coinvestement results
        self.tempDictGeneral = {}
        #temprory dictionary for clean tech VC coinvestements
        self.tempDictCleantechVC = {}

        #directories with results
        self.resdir = 'Results/'
        self.resdircleantech = 'Results/CoinvCleantechVC'

    @timer
    def parse_data_file(self):
        #get and parse data from file
        rows = csv.reader(self.csvfile, dialect='excel', delimiter=';')

        #clean energy companies and columns that we need
        for row in rows:
            self.dataCleanCompany.append(row[::5])
            self.data.append(row[0:3])

        #delete a first row with column names
        del self.data[0]

    @timer
    def data_clean_company(self):
        #we are interested only in Energy, Alternative companies so far
        self.dataCleanCompany[:] = [item[0] for item in self.dataCleanCompany if item[1] == 'Energy, Alternative']

    @timer
    def delete_cleantech_duplicates(self):
        #deletea all duplicates
        self.dataCleanCompany = set(self.dataCleanCompany)
        self.dataCleanCompany = list(self.dataCleanCompany)

    @timer
    def output_cleantech_companies(self):
        print 'Alternative energy companies: ' + str(len(self.dataCleanCompany))  + str(self.dataCleanCompany)

    @timer
    def transform_datetime(self):

        #transforme a date time
        for item in self.data:
            date_object = datetime.strptime(item[1], '%d.%m.%y')
            item[1] = date_object.year

    @timer
    def delete_data_duplicates(self):
            #delete all duplicates
            self.data.sort()
            self.data = list(self.data for self.data,_ in itertools.groupby(self.data))

    @timer
    def dictionary_construction(self):
            for item in self.data:
                #check valid data
                if item[2] != 'Undisclosed Firm' and item[2] != 'Individuals':
                    #main dictionary for targets years, VCs, companies like following {year:{VC:[Firms]}}
                    if item[1] in self.dataDic:
                        if item[2] in self.dataDic[item[1]]:
                            self.dataDic[item[1]][item[2]].append(item[0])
                        else:
                            self.dataDic[item[1]][item[2]] = [item[0]]
                    else:
                        self.dataDic[item[1]] = {}
                        self.dataDic[item[1]][item[2]] = [item[0]]
                    #dictionary for CleanTech's invested VCs
                    if item[0] in self.dataCleanCompany:
                        if item[2] in self.dataDicCleanVC:
                            if self.dataDicCleanVC[item[2]] > item[1]:
                                self.dataDicCleanVC[item[2]] = item[1]
                        else:
                            self.dataDicCleanVC[item[2]] = item[1]

    # output info for cleantech invested VCs
    @timer
    def print_cleantech_invested_VC(self):
        print 'Number of cleantech invested VCs: ' + str(len(self.dataDicCleanVC))
        print self.dataDicCleanVC

    #output all VCs that did investment in the given year
    @timer
    def print_invest_VC_year(self):
        for date in self.dates:
            print 'Year of investment: ' + str(date)
            print 'Number of companies: ' + str(len(self.dataDic[date]))


    def _output_results(self, date):
        #output results to file
        fileWrite = open(self.resdir + str(date) + '.csv', 'wb')
        writer = csv.writer(fileWrite, delimiter = ";")
        writer.writerow(["Primary VC", "Coinvested VC", "Number of companies", "Number of CleanTech"])
        for k,v in self.tempDictGeneral.items():
            writer.writerow([k[0], k[1], v[0], v[1]])

        #writer.writerows(tempDict.items())
        fileWrite.close()

    def _output_results_cleantechVC_coinvest(self, date):
        #output results for cleantech investing VCs with whom the focal VC has coinvested
        fileWrite = open(self.resdircleantech + str(date) + '.csv', 'wb')
        writer = csv.writer(fileWrite, delimiter = ";")
        writer.writerow(["Primary VC", "Number Coinvested CleanTech VC"])
        for k,v in self.tempDictCleantechVC.items():
            writer.writerow([k, len(v)])

        fileWrite.close()

    #clear temporary dictionary for a next iteration
    def _flush_tempdicts(self):
        self.tempDictGeneral.clear()
        self.tempDictCleantechVC.clear()

    @timer
    def analysis(self):
        #main cycle by date
        for date in self.dates:

            #range of dates of interest
            focalDates = [i for i in range (date-5, date)]
            # VCs in focal date
            self.tempDictTargetDate = copy.deepcopy(self.dataDic[date])

            for focalVCname, focalVCtargets in self.tempDictTargetDate.items():

                for focalDate in focalDates:
                    # if focal VC invested in previous period of time
                    if self.dataDic[focalDate].has_key(focalVCname):

                        focalVCtargetsInFocalDate = self.dataDic[focalDate][focalVCname]

                        if focalVCtargetsInFocalDate:
                            #check what companies we have
                            tempDictTargetFocalDate = copy.deepcopy(self.dataDic[focalDate])
                            # what companies are invested in this period
                            for tempVCname, tempVCtargets in self.tempDictTargetFocalDate.items():

                                if focalVCname != tempVCname:
                                    # check what ever we have common
                                    checkSet = set(focalVCtargetsInFocalDate).intersection( set(tempVCtargets) )

                                    if len(checkSet)>0:
                                        #do we have cleanTech companies out of common
                                        checkSetCleanCompany = set(self.dataCleanCompany).intersection(checkSet)
                                        # do summation
                                        if tuple([focalVCname, tempVCname]) in self.tempDictGeneral:
                                            map(operator.add, self.tempDictGeneral[tuple([focalVCname, tempVCname])], [len(checkSet),len(checkSetCleanCompany)])
                                        else:
                                            self.tempDictGeneral[tuple([focalVCname, tempVCname])] = [len(checkSet),len(checkSetCleanCompany)]
                                        # check what is a number of cleantech coinvested companies before that date
                                        if self.dataDicCleanVC.has_key(tempVCname):
                                            if self.dataDicCleanVC[tempVCname] < date:
                                                if focalVCname in self.tempDictCleantechVC:
                                                    self.tempDictCleantechVC[focalVCname].add(tempVCname)
                                                else:
                                                    self.tempDictCleantechVC[focalVCname] = set([tempVCname])

                    self.tempDictTargetFocalDate.clear()

            self.tempDictTargetDate.clear()


            #show what we have for the given date
            print 'Year of investment: ' + str(date)

            self._output_results(date)

            self._output_results_cleantechVC_coinvest(date)

            #clear temporary dictionary for a next iteration
            self._flush_tempdicts()

