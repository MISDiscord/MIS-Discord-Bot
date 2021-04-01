import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from scipy.interpolate import interp1d

date_freq = {}
with open("members.txt", "r") as f:

    for line in f.readlines():
        split = line[:11].strip().split('-')
        date = ''.join(split[::])
        try:
            date_freq[date] += 1
        except KeyError:
            date_freq[date] = 1

def check(a):
    return a[0]
print(date_freq)

l = []
for k in date_freq:
    l.append([k, date_freq[k]])

print(l)

ordered_date_list = sorted(l)

total = 0
dates = []
members = []
for i in ordered_date_list:
    total += i[1]
    members.append(total)
    dates.append(datetime.strptime(i[0], "%Y%m%d"))

print(dates)
print(members)

fig, ax = plt.subplots(figsize=(15,9))
ax.set(xlabel="Date", ylabel="Member Count", title="Current Members Older than Given Date")
date_form = DateFormatter("%Y-%m-%d")
ax.xaxis.set_major_formatter(date_form)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))

plt.plot(dates, members)

for p in [15, 150, 279, 282]:
    plt.annotate(f"({str(dates[p])[:11]}, {members[p]})",
                 (dates[p], members[p]), textcoords="offset points",
                 xytext=(-50,10), ha='center')
    plt.plot(dates[p], members[p], 'k.')
plt.show()
    
