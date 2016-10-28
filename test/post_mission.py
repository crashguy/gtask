import time

import requests

mission_list = list()

post_host = "http://172.11.51.3:9020/"

quest_list = [{
    "machine": "octq",
    "dir": 1,
    "dir_name": "sogout_data.0.comp",
    "start": 0,
    "end": 4096,
}]

for quest in quest_list:
    for i in range(quest['start'], quest['end']):
        mission_list.append({
            "job": "job",
            "name": "test-%s-%d-%04d" % (quest['machine'], quest['dir'], i),
            "docker": "r.fds.so:5000/sogou_extractor:test",
            "machine": quest['machine'],
            "command": "java -cp build/libs/sogoupreprocess.jar com.naturali.cmdline.SougouExtractor  /zfs/%s/sogout/%s/part-m-0%04d.bz2 /zfs/%s/test_out/%d/part-m-0%04d" % (
            quest['machine'], quest['dir_name'], i, quest['machine'], quest['dir'], i)
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
    print(quest['machine'] + " ends")
