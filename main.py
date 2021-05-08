import requests
import random
import json
import urllib3
import time
from PIL import Image
from io import BytesIO


urllib3.disable_warnings()
print('提示：请先在main.py中login函数输入对应账号密码哦')
print('如填写 请忽略')

url = 'https://zjy2.icve.com.cn/portal/login.html'

login_url = 'https://zjy2.icve.com.cn/api/common/login/login'

courseList_url = 'https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList'

course_url = 'https://zjy2.icve.com.cn/study/process/process.html?courseOpenId={}&openClassId={}'

process_list_url = 'https://zjy2.icve.com.cn/api/study/process/getProcessList'

get_topicId_url = 'https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId'

get_cellid_url = 'https://zjy2.icve.com.cn/api/study/process/getCellByTopicId'

view_directory_url = 'https://zjy2.icve.com.cn/api/common/Directory/viewDirectory'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

session = requests.Session()

session.headers = headers

def get_acw_tc():
    session.get(url, verify=False)

def get_code():
    r = random.random()

    src = "https://zjy2.icve.com.cn/api/common/VerifyCode/index" + "?t=" + str(r)

    res = session.get(src, verify=False)
    
    img = res.content

    with open('verifycode.png', 'wb') as f:
        f.write(img)
        img = Image.open(BytesIO(img))
        img.show()

def login():
    verifyCode = input('输入验证码：')
    data = {
        'userName': '*******',
        'userPwd': '*******',
        'verifyCode': verifyCode
    }
    res = session.post(login_url, data=data, verify=False)

    userId = res.json()['userId']  # stuId
    schoolId = res.json()['schoolId']
    token = res.json()['token']

    return userId, schoolId, token

def get_course_list():

    res = session.post(courseList_url, verify=False)
    # 课程信息
    courseList = res.json()['courseList']
    return courseList

def choose(courseList):
    for i in range(len(courseList)):
        course = courseList[i]
        courseName = course['courseName']

        print(str(i+1) +'--'+ courseName)

def into_course(courseList, time_start):
    i = int(input('请选择你要刷的课程：')) - 1
    course = courseList[i]

    courseOpenId = course['courseOpenId']
    openClassId = course['openClassId']

    params = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId
    }

    session.get(course_url, params=params, verify=False)

    #　课件信息
    process_list = get_process_list(courseOpenId, openClassId)

    # 与课件第一个id一样
    # moduleId = process_list['progress']['moduleId']
    # 课件列表
    module_list = process_list['progress']['moduleList']

    for i in range(len(module_list)):
        # 每个课件
        module = module_list[i]
        # 课件id
        module_id = module['id']
        # 目录
        module_name = module['name']
        # 进度
        module_percent = module['percent']

        print(i+1, '  ', module_name , '  进度：' , module_percent)

    i = int(input('请选择你要刷章节(输入‘0’表示全选)：'))
    if i != 0:
        while True:
            # 每个课件
            module = module_list[i-1]
            # 课件id
            module_id = module['id']
            # 目录
            module_name = module['name']
            # 进度
            module_percent = module['percent']
            # 子目录列表
            topicList = get_topicId(courseOpenId, module_id, openClassId)

            for o in range(len(topicList)):
                # 每个课件中 小课件id
                topicId = topicList[o]['id']
                # upTopicId = topicList[o]['upTopicId']

                # 文件列表
                cellList = get_cellid(courseOpenId, openClassId, topicId) 
            
                for p in range(len(cellList)):
                    # 文件
                    cell = cellList[p]

                    cellId = cell['Id']
                    # upCellId = cell['upCellId']
                    cellName = cell['cellName']
                    categoryName = cell['categoryName']  # 文件名称
                    stuCellPercent = cell['stuCellPercent']

                    if stuCellPercent == 100:
                        print(cellName + '进度100%  跳过')  
                        time.sleep(1)
                        continue
                    
                    if categoryName == '子节点':
                        childNodeList = cell['childNodeList']
                        for n in range(len(childNodeList)):
                            childNode = childNodeList[n]
                            cellId = childNode['Id']
                            # upCellId = cell['upCellId']
                            cellName = childNode['cellName']
                            categoryName = childNode['categoryName']  # 文件名称
                            stuCellPercent = cell['stuCellPercent']

                            
                            if categoryName == '视频' or categoryName == '音频':
                                # 进入播放页面
                                # return 当前观看信息
                                res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                                cellLogId = res['cellLogId']
                                cellLogId = 'test'
                                audioVideoLong = res['audioVideoLong']
                                stuStudyNewlyTime = res['stuStudyNewlyTime']
                                cellPercent = res['cellPercent']
                                print('视频进度---' + str(cellPercent))
                                print('开始！！！')
                                video(courseOpenId, openClassId, cellId, cellLogId,stuStudyNewlyTime, audioVideoLong, time_start)
                                add_view_content(courseOpenId, openClassId, cellId, cellName)

                            elif categoryName == 'ppt' or  categoryName == '文档':
                                # 进入播放页面
                                res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                                cellLogId = res['cellLogId']
                                cellLogId = 'test'
                                pageCount = res['pageCount']
                                cellPercent = res['cellPercent']
                                stuCellViewTime = res['stuCellViewTime']

                                if int(cellPercent) == 100:
                                    print('文件进度100% 评论功能开启...')
                                    add_view_content(courseOpenId, openClassId, cellId, cellName)
                                    time.sleep(1)
                                    continue
                                print('ppt-or-office文档 已就绪!!!')
                                print('之前总学习时间：' + str(stuCellViewTime))
                                #　刷ppt
                                ppt(courseOpenId, openClassId, cellId, cellLogId, pageCount, time_start)
                                res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                                stuCellViewTime = res['stuCellViewTime']
                                print('现在总文件学习时间：' +  str(stuCellViewTime))
                                add_view_content(courseOpenId, openClassId, cellId, cellName)
                            else:
                                print(' Warning：{}-该文件非 视频 or ppt or office文档！'.format(cellName))
                                print(' 跳过 ')
                                time.sleep(2)
                                continue
                            time.sleep(2)
                         
                         
                    if categoryName == '视频' or categoryName == '音频':
                        # 进入播放页面
                        # return 当前观看信息
                        res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                        cellLogId = res['cellLogId']
                        cellLogId = 'test'
                        audioVideoLong = res['audioVideoLong']
                        stuStudyNewlyTime = res['stuStudyNewlyTime']
                        cellPercent = res['cellPercent']
                        print('视频进度---' + str(cellPercent))
                        print('开始！！！')
                        video(courseOpenId, openClassId, cellId, cellLogId,stuStudyNewlyTime, audioVideoLong, time_start)
                        add_view_content(courseOpenId, openClassId, cellId, cellName)

                    elif categoryName == 'ppt' or  categoryName == '文档':
                        # 进入播放页面
                        res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                        cellLogId = res['cellLogId']
                        cellLogId = 'test'
                        pageCount = res['pageCount']
                        cellPercent = res['cellPercent']
                        stuCellViewTime = res['stuCellViewTime']

                        if int(cellPercent) == 100:
                            print('文件进度100% 评论功能开启...')
                            add_view_content(courseOpenId, openClassId, cellId, cellName)
                            time.sleep(1)
                            continue
                        print('ppt-or-office文档 已就绪!!!')
                        print('之前总学习时间：' + str(stuCellViewTime))
                        #　刷ppt
                        ppt(courseOpenId, openClassId, cellId, cellLogId, pageCount, time_start)
                        res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                        stuCellViewTime = res['stuCellViewTime']
                        print('现在总文件学习时间：' +  str(stuCellViewTime))
                        add_view_content(courseOpenId, openClassId, cellId, cellName)
                    else:
                        print(' Warning：{}-该文件非 视频 or ppt or office文档！'.format(cellName))
                        print(' 跳过 ')
                        time.sleep(2)
                        continue
                    time.sleep(2)
                time.sleep(2)
                # break       
            time.sleep(2)
            # break
            for i in range(len(module_list)):
	            # 每个课件
	            module = module_list[i]
	            # 课件id
	            module_id = module['id']
	            # 目录
	            module_name = module['name']
	            # 进度
	            module_percent = module['percent']

	            print(i+1, '  ', module_name , '  进度：' , module_percent)
            
            i = int(input('请选择你要刷章节：'))

            
    else:
        for i in range(len(module_list)):
            # 每个课件
            module = module_list[i]
            # 课件id
            module_id = module['id']
            # 目录
            module_name = module['name']
            # 进度
            module_percent = module['percent']
            
            # 如果目录进度100% 跳过
            if str(module_percent) == '100.0':
                print(module_name + '  该目录进度100%  跳过')
                time.sleep(1)
                continue
            
            # 子目录列表
            topicList = get_topicId(courseOpenId, module_id, openClassId)

            for o in range(len(topicList)):
                # 每个课件中 小课件id
                topicId = topicList[o]['id']
                # upTopicId = topicList[o]['upTopicId']

                # 文件列表
                cellList = get_cellid(courseOpenId, openClassId, topicId) 
            
                for p in range(len(cellList)):
                    # 文件
                    cell = cellList[p]

                    cellId = cell['Id']
                    # upCellId = cell['upCellId']
                    cellName = cell['cellName']
                    categoryName = cell['categoryName']  # 文件名称
                    stuCellPercent = cell['stuCellPercent']

                    if stuCellPercent == 100:
                        print(cellName + '进度100%  跳过')  
                        time.sleep(1)
                        continue

                    if categoryName == '视频' or categoryName == '音频':
                        # 进入播放页面
                        # return 当前观看信息
                        res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                        cellLogId = res['cellLogId']
                        cellLogId = 'test'
                        audioVideoLong = res['audioVideoLong']
                        stuStudyNewlyTime = res['stuStudyNewlyTime']
                        cellPercent = res['cellPercent']
                        print('视频进度---' + str(cellPercent))
                        print('开始！！！')
                        video(courseOpenId, openClassId, cellId, cellLogId,stuStudyNewlyTime, audioVideoLong, time_start)
                        add_view_content(courseOpenId, openClassId, cellId, cellName)

                    elif categoryName == 'ppt' or  categoryName == '文档':
                        # 进入播放页面
                        res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                        cellLogId = res['cellLogId']
                        cellLogId = 'test'
                        pageCount = res['pageCount']
                        cellPercent = res['cellPercent']
                        stuCellViewTime = res['stuCellViewTime']

                        if int(cellPercent) == 100:
                            print('文件进度100% 评论功能开启...')
                            add_view_content(courseOpenId, openClassId, cellId, cellName)
                            time.sleep(1)
                            continue
                        print('ppt-or-office文档 已就绪!!!')
                        print('之前总学习时间：' + str(stuCellViewTime))
                        #　刷ppt
                        ppt(courseOpenId, openClassId, cellId, cellLogId, pageCount, time_start)
                        res = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
                        stuCellViewTime = res['stuCellViewTime']
                        print('现在总文件学习时间：' +  str(stuCellViewTime))
                        add_view_content(courseOpenId, openClassId, cellId, cellName)
                    else:
                        print(' Warning：{}-该文件非 视频 or ppt or office文档！'.format(cellName))
                        print(' 跳过 ')
                        time.sleep(2)
                        continue
                    time.sleep(2)
                time.sleep(2)
                # break       
            time.sleep(2)
            # break

def get_process_list(courseOpenId, openClassId):
    params = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId
    }
    
    res = session.post(process_list_url, params=params, verify=False).json()

    return res

def get_topicId(courseOpenId, moduleId, openClassId):
    params = {
        'courseOpenId': courseOpenId,
        'moduleId': moduleId
    }

    res = session.post(get_topicId_url, headers=headers, params=params)

    return res.json()['topicList']

def get_cellid(courseOpenId, openClassId, topicId):
    params = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'topicId': topicId
    }
    res = session.post(get_cellid_url, params=params, verify=False)
    
    return res.json()['cellList']

def get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName):
    params = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'cellId': cellId,
        'flag': 's',
        'moduleId': module_id
    }

    res = session.post(view_directory_url, params=params, verify=False)
    time.sleep(1)
    if res.json()['code'] == -100 or res.json()['code'] == '-100':
        #print('在你进入view_dectory页面时 会提示你 上次课件进度多少 你这次选择的进度多少')
        #print('需要你选择 所以代码进入是code会变为-100 你需要请求另一个地址转化一下  抓包得到 fidder 谷歌浏览器抓不到(好像有其他几个地址也是)')
        #print('code=-100')
        changeCellData(courseOpenId, openClassId, module_id, cellId, cellName)
        res1 = get_view_directory(courseOpenId, openClassId, cellId, module_id, cellName)
        return res1
        
    return res.json()

def changeCellData(courseOpenId, openClassId, moduleId, cellId, cellName):
    url = 'https://zjy2.icve.com.cn/api/common/Directory/changeStuStudyProcessCellData'
    
    data = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'moduleId': moduleId,
        'cellId': cellId,
        'cellName': cellName
    }
    
    session.post(url, data=data, verify=False)

def add_view_content(courseOpenId, openClassId, cellId, cellName):
    if random.randint(1, 100) >= 20:
        return 0
    url = 'https://zjy2.icve.com.cn/api/common/Directory/addCellActivity'
    print('文件：' + cellName + '---评论开始......(每篇需要数分钟！！！)')
    print('Reason 由于PC端服务器的限制！！！')
    data1 = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'cellId': cellId,
        'content': '<span style="color: rgb(51, 51, 51); background-color: rgb(255, 255, 255);">{}</span>'.format(random.choice(['课程讲的非常好', '好', 'hao', '课程思路清晰，环节紧凑'])),
        'docJson': '',
        'star': '5',
        'activityType': '1'
    }

    if random.randint(1, 2) == 2:
        session.post(url, data=data1, verify=False)
        time.sleep(20)

    data2 = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'cellId': cellId,
        'content': '{}'.format(random.choice(['无', '非常好', '好'])),
        'docJson': '',
        'star': '0',
        'activityType': '3'
    }

    if random.randint(1, 2) == 2:
        session.post(url, data=data2, verify=False)
        time.sleep(20)

    data3 = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'cellId': cellId,
        'content': '{}'.format(random.choice(['学到许多', '非常好', '好'])),
        'docJson': '',
        'star': '0',
        'activityType': '2'
    }

    if random.randint(1, 2) == 2:
        session.post(url, data=data3, verify=False)
        time.sleep(20)

    data4 = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'cellId': cellId,
        'content': '{}'.format(random.choice(['无', '错误已更正', '好'])),
        'docJson': '',
        'star': '0',
        'activityType': '4'
    }

    if random.randint(1, 2) == 2:
        session.post(url, data=data4, verify=False)
        print('Success ' + cellName + '-'*10+'增加..评论..问答..笔记..纠错..已完成'+ '-'*10)

def video(courseOpenId, openClassId, cellId, cellLogId, stuStudyNewlyTime, audioVideoLong, time_start):
    '''
        刷视频
        通过抓包分析, 网页观看视频就是隔断时间对这个地址发送请求
        studyNewlyTime就是当前视频播放的进度数
        我设置的是10秒发送一次请求 谷歌抓包发现也是10秒
        Notice：
            发送间隔为10秒, 所以当前视频播放的进度数与上次发送的进度数相减约等于10, 不然嗝屁, 会封该课件--也没多久
    '''
    url = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'

    forNum = int((audioVideoLong - stuStudyNewlyTime) / 10) # 循环次数 总视频长度-观看过后的长度分10段 每段循环后会加10.多

    for i in range(forNum):
        if stuStudyNewlyTime-1 < 0:
            stuStudyNewlyTime = 1
            
        Percent = stuStudyNewlyTime - 1 + 10.0000001*i

        if Percent >= audioVideoLong: # 怕超过视频总长度, 不晓得会出啥事
            o = audioVideoLong
        else:
            o = Percent

        params = {
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'cellId': cellId,
            'cellLogId': cellLogId,
            'picNum': 0,
            'studyNewlyTime': o,
            'studyNewlyPicNum': 0
            # 'token': ''
        }

        r = session.post(url, params=params, verify=False).json()
        if r['code'] == 1 or r['code'] == '1':
            run_time = time.gmtime((time.mktime(time.localtime(time.time())) - time.mktime(time_start)))
            print(" ",time.strftime('%H:%M:%S   ',time.localtime(time.time())),time.strftime('已经运行： %H:%M:%S   ', run_time),' 视频 学习总时间增加！')
        else:
            print('Warning 视频时间增加出错')
            exit()
            
        if Percent >= audioVideoLong:
            break
            
        time.sleep(5)

def ppt(courseOpenId, openClassId, cellId, cellLogId, pageCount, time_start):
    '''
        刷ppt
        通过抓包分析, 网页观看视频就是隔断时间对这个地址发送请求
        为什么我要循环呢
        因为我发现每次发个请求, (/viewDirectory)地址返回数据中有个时间会增加10
        我猜是学习课件时间
    '''
    url = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'
    num = random.randint(3, 6)
    o = pageCount - num + 1

    for i in range(num):
        params = {
        'courseOpenId': courseOpenId,
        'openClassId': openClassId,
        'cellId': cellId,
        'cellLogId': cellLogId,
        'picNum': o+i,
        'studyNewlyTime': '0',
        'studyNewlyPicNum': o+i
        # 'token': ''
        }

        res = session.post(url, params=params, verify=False).json()
        if res['code'] == 1:
            run_time = time.gmtime((time.mktime(time.localtime(time.time())) - time.mktime(time_start)))
            print(" ",time.strftime('%H:%M:%S   ',time.localtime(time.time())),time.strftime('已经运行： %H:%M:%S   ', run_time),'ppt加载成功 学习总时间增加！')
        time.sleep(1)


if __name__ == "__main__":
    get_acw_tc()

    get_code()

    userId, schoolId, token = login()

    courseList = get_course_list()

    choose(courseList)

    time_start = time.localtime(time.time())
    into_course(courseList, time_start)