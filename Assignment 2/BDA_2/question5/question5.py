from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import functions as F
import sys
def toCSVLine(data):
  return "\t".join(str(d) for d in data)

if __name__ == "__main__":
    sc = SparkContext(appName="Question5")
    sqlContext = SQLContext(sc)
    business_raw = sc.textFile(sys.argv[1] + sys.argv[2])
    business_project = business_raw.map(lambda line: line.split("::")).flatMap(lambda record: record[2][5:len(record[2])-1].split(",")).map(lambda word : (word,0) if word =="" else (word,1)).reduceByKey(lambda a,b:a+b).map(lambda x:(x[1],x[0])).sortByKey(False).map(toCSVLine)
    
    business_project.saveAsTextFile(sys.argv[1] + sys.argv[3])
	
