import random
import math
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def read():
    with open('messagecount.txt') as f:
        for i in f.readlines():
            obj = i.strip().split(" ")
            #print(range(int(obj[0])))
            id = obj[1]
            xp = 0
            for i in range(int(obj[0])):
                xp += 10 + math.ceil(random.random()*5)
            #print([id, xp])
            return [id, xp]

x = 0
n = 50000
values = []
for i in range(0,n):
    values.append(read()[1])

for i in values:
    x += i

mean = x/n

N_stddev_sqrd = 0

for i in values:
    N_stddev_sqrd += (i - mean)**2

std = np.sqrt(N_stddev_sqrd/n)
print(std)
print(mean)
print(values)

kwargs = dict(hist_kws={'alpha':.6}, kde_kws={'linewidth':2})

plt.figure(figsize=(10,7), dpi=80)
sns.distplot(values, color="dodgerblue", label="XP", **kwargs)
plt.legend()
plt.show()
