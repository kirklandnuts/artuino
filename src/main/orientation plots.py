import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

path0 = "/Users/timmy/Documents/projects/artuino/data/test1.csv"
path1 = "/Users/timmy/Documents/projects/artuino/data/test0.csv"
path2 = "/Users/timmy/Documents/projects/artuino/data/test2.csv"

pathroll = "/Users/timmy/Documents/projects/artuino/data/testroll.csv"
pathroll1 = "/Users/timmy/Documents/projects/artuino/data/testroll1.csv"
pathroll2 = '/Users/timmy/Documents/projects/artuino/data/testroll2.csv'

pathyaw = '/Users/timmy/Documents/projects/artuino/data/testyaw.csv'
pathyaw1 ="/Users/timmy/Documents/projects/artuino/data/testyaw1.csv"

pathpitch ='/Users/timmy/Documents/projects/artuino/data/testyaw1.csv'


df = pd.read_csv(path0)
df1 = pd.read_csv(path1)
df2 = pd.read_csv(path2)

dfroll = pd.read_csv(pathroll)
dfroll1 = pd.read_csv(pathroll1)
dfroll2 = pd.read_csv(pathroll2)

dfyaw = pd.read_csv(pathyaw)
dfyaw1 = pd.read_csv(pathyaw1)

dfpitch = pd.read_csv(pathpitch)


# 0 plots
pitchplt = plt.plot(df['pitch'])

yawplt = plt.plot(df['yaw'])
yawplt = plt.ylim(-60,-40)



rollplt = plt.plot(df['roll'])
rollplt2 = plt.plot(df2['roll'])

yawplt = plt.plot(dfyaw1['yaw']) #calculate change