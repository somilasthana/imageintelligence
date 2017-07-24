from sklearn.externals import joblib

fp = open('/home/centos/caffe/data/map_clsloc.txt')
hmap = {}
for line in fp:
    rline = line.strip()
    token = rline.split(' ')
    #print(token[0], token[2].lower())
    hmap.setdefault(token[0], token[2].lower())

joblib.dump(hmap, '/home/centos/caffe/data/metadata.pkl')

mapping = joblib.load('/home/centos/caffe/data/metadata.pkl')
#mapping

import pandas as pd
df = pd.read_csv("/home/centos/caffe/data/ilsvrc12/synset_words.txt", sep='\s{2,}', engine='python', names=['col'])

df['class'] = df['col'].str.split().apply(lambda x: x[0])

df['class'].values

joblib.dump(df['class'].values, '/home/centos/caffe/data/label.pkl')
