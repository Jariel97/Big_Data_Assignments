
from pyspark import SparkContext, SparkConf
import sys


def make_pairs(line):
    user1 = line[0].strip()
    friend_list = line[1]
    if user1 != '':
        all_pairs = []
        for friend in friend_list:
            friend = friend.strip()
            if friend != '':
                if float(friend) < float(user1):
                    pairs = (friend + "," + user1, set(friend_list))
                else:
                    pairs = (user1 + "," + friend, set(friend_list))
                all_pairs.append(pairs)
        return all_pairs
def toCSVLine(data):
  return "\t".join(str(d) for d in data)

if __name__ == "__main__":
    config = SparkConf().setAppName("Question2").setMaster("local[2]")
    sc = SparkContext(conf=config)

    friends = sc.textFile(sys.argv[1] + sys.argv[2]).map(lambda x: x.split("\t")).filter(lambda x: len(x) == 2).map(lambda x: [x[0], x[1].split(",")])

    friend_pairs = friends.flatMap(make_pairs)
    common_friends = friend_pairs.reduceByKey(lambda x, y: x.intersection(y)).map(lambda x:(x[0],len(x[1]))).coalesce(1).map(lambda x:(x[1],x[0])).sortByKey(False)
    maxi=list(common_friends.take(1))
    
    maxi=maxi[0][0]
    common_friends=common_friends.map(lambda x : (x[1],x[0]) if (x[0]>=maxi) else "#").collect() 
    common_friends= set(common_friends)
    common_friends.remove("#")
    
    sc.parallelize(common_friends).saveAsTextFile(sys.argv[1] + sys.argv[3])
