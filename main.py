__author__ = 'sergeygolubev'

from VCStatisticsDic import VCAnalysis
from GraphAnalysis import DataAnalysis


def main():

    vcAnls = VCAnalysis('Data/data.csv', 1990, 2012)

    vcAnls.parse_data_file()
    vcAnls.data_clean_company()
    vcAnls.delete_cleantech_duplicates()
    vcAnls.output_cleantech_companies()
    vcAnls.transform_datetime()
    vcAnls.delete_data_duplicates()
    vcAnls.dictionary_construction()
    vcAnls.print_cleantech_invested_VC()
    vcAnls.print_invest_VC_year()
    vcAnls.analysis()

    dataAnls = DataAnalysis(sourcedir='Results/', resultdir='ResultsGraphWeighted/', startdate=2005)
    dataAnls.process()

if __name__ == "__main__":
    main()