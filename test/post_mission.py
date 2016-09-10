import requests
import time
mission_list = list()

post_host = "http://10.8.0.46:9020/"

for i in range(0, 3688):
    mission_list.append({
        "job": "job",
        "name": "test-%04d" % i,
        "docker": "r.fds.so:5000/sogou_extractor:test",
        "machine": "octp",
        "command": "java -cp build/libs/sogoupreprocess.jar com.naturali.cmdline.SougouExtractor  /zfs/octp/sogout/1/part-m-0%04d.bz2 /zfs/octp/test_out/part-m-0%04d" % (i, i)
    })

    if len(mission_list) >= 100:
        r = requests.post(url=post_host + "mission/", json=mission_list)
        r = r.json()
        print(r)
        mission_list.clear()
        time.sleep(1)
        print(i)

r = requests.post(url=post_host + "mission/", json=mission_list)
r = r.json()
print(r)
mission_list.clear()
time.sleep(1)
print(i)