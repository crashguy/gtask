提交cpu计算任务

POST http://172.11.51.3:9020/mission/
post data:
```json
[{
	"job": "job-1",
	"name": "test",
	"docker": "r.fds.so:5000/sogou_extractor:test",
	"machine": "octp",
	"command": "java -cp build/libs/sogoupreprocess.jar com.naturali.cmdline.SougouExtractor  /zfs/octp/sogout/1/part-m-00000.bz2 /zfs/octp/test_out/part-m-00000"
}]
```
* job: 任务批次
* name: 单个任务名称,不能重复
* docker: docker image
* machine: 运行的机器, 最好与文件位置相同
* command: 执行的命令.


respanse:
```json
{'failed_missions': [
	"<mission with failed reason>", 
	"<mission with failed reason>"
]}
```

examples:
https://github.com/crashguy/gtask/blob/master/test/post_mission.py
