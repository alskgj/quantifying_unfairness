from scipy.interpolate import spline
import numpy

# raw data
times = [0.0, 3.0, 3.0, 4.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0]
sizes = [0.220423, 0.148095, 0.14781, 0.233517, 0.001156, 0.000285, 0.001147, 0.165771, 0.608256, 0]

distinct_times = set(times)
new = []
#for distinct_time in distinct_times:
#    new.append((distinct_time, sum(size*8 for time, size in combined if time == distinct_time)))
for i in range(int(max(distinct_times))+1):
    if i in distinct_times:
        new.append((i, sum(size*8 for time, size in zip(times, sizes) if time == i)))
    else:
        new.append((i, 0))

print(new)
times, sizes = [e[0] for e in new], [e[1] for e in new]
interpolator = spline(times, sizes, range(0, int(times[-1])+1, 2))

print(interpolator)


