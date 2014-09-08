__author__ = 'sergeygolubev'

import csv
import networkx as nx
import matplotlib.pyplot as plt
import timer
import time
from timer import timer

class DataAnalysis:

    def __init__(self, sourcedir='Results/', resultdir='ResultsGraph/', startdate=1990, enddate=2013):

        #list with dates always on one greater
        self.dates = [i for i in range (startdate, enddate)]

        self.srcdir = sourcedir
        self.rstdir = resultdir

        self.G=nx.Graph()

    def _save_result(self, date, data):

        resultdic={}

        for dt in data:
            for k, v in dt.items():
                if k in resultdic:
                    resultdic[k].append(v)
                else:
                    resultdic[k] = []
                    resultdic[k].append(v)

        with open(self.rstdir + str(date) + '.csv', 'wb') as fileWrite:
            writer = csv.writer(fileWrite, delimiter = ";")
            writer.writerow(["VC", "Eigenvector_centrality", "Betweenness_centrality", "Closeness_centrality",
                             "Degree_centrality", "Communicability_centrality" ])

            for k,v in resultdic.items():
                writer.writerow([k, v[0], v[1], v[2], v[3], v[4]])


    def _save_graph_gexf(self, date):
        nx.write_gexf(self.G, self.rstdir + str(date) + '.gexf')

    @timer
    def process(self):

        for date in self.dates:

            print "Year of analysis " + str(date)

            rst = []

            with open(self.srcdir + str(date) + '.csv', 'rU') as f:
                rows = csv.reader(f, dialect='excel', delimiter=';')
                next(rows, None)
                for row in rows:

                    self.G.add_node(row[0])
                    self.G.add_node(row[1])
                    self.G.add_edge(row[0], row[1], weight=float(row[2]))
                    # self.G.add_edge(row[0], row[1])
                    # self.G.add_edge(row[0], row[1], weight=abs(float(float(row[3])/float(row[2]))))

            rst.append(nx.eigenvector_centrality_numpy(self.G))
            rst.append(nx.betweenness_centrality(self.G))
            rst.append(nx.closeness_centrality(self.G))
            rst.append(nx.degree_centrality(self.G))
            rst.append(nx.communicability_centrality(self.G))

            self._save_result(date, rst)
            self._save_graph_gexf(date)
