from math import sqrt
import numpy as np
from numpy import array
import pyspark
from pyspark import *
from pyspark.conf import *
from pyspark.sql import *
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import KMeans


itemusermatdata_path = '/input/itemusermat.data'
num_cluster = 10
moviesdata_path = '/input/movies.dat'
spark = SparkConf().setAppName("K-Means").setMaster("local")
sc = SparkContext(conf=spark)
sc.setLogLevel("ERROR")
def movies_line_mapper(line):
    data = line.split('::')
    data[0] = float(data[0])
    data[2] = data[2].split('|')
    genre = ''
    for i in data[2]:
        genre += i + ', '

    genre = genre[:-2]
    data[2] = genre
    return (data[0], data[1:])

def itemuser_mat_mapper(line):
    data = line.split(' ')
    n = len(data)

    for i in range(n):
        data[i] = float(data[i])
    return data

itemuser_data_rdd = sc.textFile(itemusermatdata_path)
parsed_itemuser_data = itemuser_data_rdd.map(itemuser_mat_mapper)
data = parsed_itemuser_data.collect()
moviesdata_rdd = sc.textFile(moviesdata_path)
parsed_movies_data = moviesdata_rdd.map(movies_line_mapper)
data = parsed_movies_data.collect()

kmeansModel = KMeans.train(parsed_itemuser_data, num_cluster, maxIterations=500)

predicted_data = kmeansModel.predict(parsed_itemuser_data)

def combine_rdds_mapper(x):
    temp = np.append(x[0], x[1])
    return (temp[0], temp[-1])

itemuser_prediction_rdd = parsed_itemuser_data.zip(predicted_data).map(combine_rdds_mapper)

combined_data_rdd = itemuser_prediction_rdd.join(parsed_movies_data).map(lambda line: (line[0], line[1][0], line[1][1]))


final_data_rdd = combined_data_rdd.groupBy(lambda line: line[1]).sortByKey(True).map(
    lambda line: (line[0], list(line[1])[1:6]))
with open('question2.txt', 'w') as f:
    for i in final_data_rdd.take(10):
        f.write('Cluster ' + str(int(i[0]) + 1) + '\n')
        for j in i[1]:
            f.write(str(int(j[0])) + ' ' + j[2][0] + ' ' + j[2][1] + '\n')
        f.write('\n\n\n')
f.close()






