# import jobs as jd

# jd.bytedance_jobs()

# import jobs

# jobs.bytedance_jobs()

# from jobs import bytedance_jobs

# bytedance_jobs()

from jobs import bytedance_jobs as bdj
import time
import random
random.seed(time.time())
for i in range(1000):
    bdj(i*10)# 0,10,20,30,40,50,60,70,80,90,100
    time.sleep(random.randint(1,5))
    