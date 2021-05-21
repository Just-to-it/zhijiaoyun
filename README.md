```
    author: 热狗得小舔狗
    createtTime: 2021-1-3
    updateTime:  2021-5-21
```

# 免责声明：此代码仅供学习使用，任何使用与作者无关


##### 创作来之不易, mooc学院代码奋战几天, 无利益挂钩, 希望大家多给小星星就行！ 

#### 更新说明 2021-5-21
1. 新增mooc.py, 为职教mooc学院脚本.
    1. 支持视频, 音频, ppt, 文档, 图片, 讨论, 子节点(大致于职教云类似)
    2. 新增作业/测试答题
        1. 只支持作业/测试答题次数大于等于2或无限次
        2. 答题时间已过/只能答一次/有简答题/需要老师批改, 不支持,程序自动跳过
        3. 考试不支持
        
2. mooc.py使用
    1. 在代码27-32完成你的账号密码信息配置
    2. cmd中输入python mooc.py
    3. 输入验证码

3. zjy.py使用
    1. cmd中输入python zjy.py
    2. 输入账号, 密码, 选择是否评论
    3. 输入验证码

3. 问题
    1. 职教云,mooc学院多开问题
        1. 不同账号可以多开
        2. 一边刷职教云一边mooc学院不冲突,可多开
        3. 须注意：多开需要网速支持, 如开的过多, 会导致请求超时程序报错
    
    2. 报错问题
        1. json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)此报错最为常见, 报错后,尽量休息十分钟再次开始
        2. 请求超时报错, 一大串有三段, 一般为网速问题


#### 更新说明 2021-5-12
1. 新增刷图片, 各种文档
2. 新增实现有带"子节点"这种目录的
3. 新增是否需要评论
4. sleep数量和时间增加, 更稳点吧



#### 更新说明 2021-4-23
今天更新了一下, 主要包括以下几点：
1. 登录方式不明确(解决)
2. 刷视频不是100%, 差很多(解决)
3. 评论时间过长(大幅缩减)
4. 代码重写了一下


##### 感谢
首先谢谢大家的小星星, 也感谢使用的小伙伴提出的宝贵意见, xiexie 哈哈！
希望大家多给小星星(^_^)


##### 使用说明
1. 首先要有python环境啦
2. pip install requests -i https://mirrors.tuna.tsinghua.edu.cn/
3. pip install urllib3 -i https://mirrors.tuna.tsinghua.edu.cn/
4. random json time好像不需要install
5. 打开cmd窗口
6. 输入python main.py 即可
