
import sys
import itertools
from math import sqrt
from operator import add
from os.path import join, isfile, dirname
from pyspark import SparkConf, SparkContext
from pyspark.mllib.recommendation import ALS

def parseRating(line):
    fields = line.strip().split("::")
    return int(fields[3]) % 10, (int(fields[0]), int(fields[1]), float(fields[2]))

def parseMovie(line):
    fields = line.strip().split("::")
    return int(fields[0]), fields[1]

def loadRatings(ratingsFile):
    f = open(ratingsFile, 'r')
    ratings = filter(lambda r: r[2] > 0, [parseRating(line)[1] for line in f])
    f.close()
    return ratings

def computeRmse(model, data, n):
    predictions = model.predictAll(data.map(lambda x: (x[0], x[1])))
    predictionsAndRatings = predictions.map(lambda x: ((x[0], x[1]), x[2])) \
      .join(data.map(lambda x: ((x[0], x[1]), x[2]))) \
      .values()
    return sqrt(predictionsAndRatings.map(lambda x: (x[0] - x[1]) ** 2).reduce(add) / float(n))

if __name__ == "__main__":
    conf = SparkConf() \
      .setAppName("Question3") \
      .set("spark.executor.memory", "2g")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    myRatings = loadRatings(sys.argv[2])
    myRatingsRDD = sc.parallelize(myRatings, 1)
    hdfsDir = sys.argv[1]
    ratings = sc.textFile(join(hdfsDir, "ratings.dat")).map(parseRating)
    movies = dict(sc.textFile(join(hdfsDir, "movies.dat")).map(parseMovie).collect())
    numRatings = ratings.count()
    numUsers = ratings.values().map(lambda r: r[0]).distinct().count()
    numMovies = ratings.values().map(lambda r: r[1]).distinct().count()
    print ("Got %d ratings from %d users on %d movies." % (numRatings, numUsers, numMovies))
    numPartitions = 4
    training = ratings.filter(lambda x: x[0] < 7) \
      .values() \
      .union(myRatingsRDD) \
      .repartition(numPartitions) \
      .cache()

    validation = ratings.filter(lambda x: x[0] >= 7 and x[0] < 9) \
      .values() \
      .repartition(numPartitions) \
      .cache()

    test = ratings.filter(lambda x: x[0] >= 7).values().cache()

    numTraining = training.count()
    numValidation = validation.count()
    numTest = test.count()

    print ("Training: %d, validation: %d, test: %d" % (numTraining, numValidation, numTest))

    ranks = [8,12,16,20]
    lambdas = [0.1,1.0,10.0]
    numIters = [10, 20]
    bestModel = None
    bestValidationRmse = float("inf")
    bestRank = 0
    bestLambda = -1.0
    bestNumIter = -1

    for rank, lmbda, numIter in itertools.product(ranks, lambdas, numIters):
        model = ALS.train(training, rank, numIter, lmbda)
        validationRmse = computeRmse(model, validation, numValidation)
        print ("RMSE = %f for the model trained with " % validationRmse + \
              "rank = %d, lambda = %.4f, and iteration = %d." % (rank, lmbda, numIter))
        if (validationRmse < bestValidationRmse):
            bestModel = model
            bestValidationRmse = validationRmse
            bestRank = rank
            bestLambda = lmbda
            bestNumIter = numIter

    testRmse = computeRmse(bestModel, test, numTest)

    print ("The best model was trained with rank = %d and lambda = %.4f, " % (bestRank, bestLambda) \
      + "and iteration = %d, and its RMSE on the test set is %f." % (bestNumIter, testRmse))
    meanRating = training.union(validation).map(lambda x: x[2]).mean()
    baselineRmse = sqrt(test.map(lambda x: (meanRating - x[2]) ** 2).reduce(add) / numTest)
    improvement = (baselineRmse - testRmse) / baselineRmse * 100
    print ("The best model improves the baseline by %.4f" % (improvement) + "%.")
    sc.stop()
