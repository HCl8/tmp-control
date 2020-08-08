import datetime


# 1档：0.8/分，2档：1度/分，3档：1.2度/分。每度电5元

# 房间号、记录起止时间、起止时间内风速、起止时间内风量大小等。

def initial():
    return ['', '', '', '', 0, 0, 0, 0]


# 返回值report格式
# [[slavemessage], cost]
# 从控机消息列表，总费用(float)
#
# slavemessage格式
# [slaveid,ontimes, offtimes, [message]]
# 从控机id，开启次数(int)，关闭次数(int)，每次启动详细信息列表
#
# message格式
# [questtime, finishtime, nowtemp, targettemp, num1, num2, num3, thiscost]
# 开始时间,结束时间,开始温度,目标温度,1档数(int),2档数(iny),3档数(int),本次风量(float)

def getReport():
    date = datetime.datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    path = "save/master/" + date_str + '.log'
    time = []
    tag = []
    content = []
    with open(path, 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            temp = line.strip().split(':')
            time.append(temp[0])
            tag.append(temp[1])
            content.append(temp[2])
    f.close()

    report = []
    slave = []
    ontimes = []
    offtimes = []
    information = []
    # 开始时间,结束时间,开始温度,目标温度,1档数,2档数,3档数,本次花费
    message = ['', '', '', '', 0, 0, 0, 0]
    mid = []

    path = "save/slave/" + date_str + '.log'
    with open(path, 'r', encoding='UTF-8') as f:
        oncheck = []
        for line in f.readlines():
            temp = line.strip().split(':')
            if temp[1] == 'on':
                if temp[2] not in slave:
                    slave.append(temp[2])
                    information.append([])
                    ontimes.append(1)
                    offtimes.append(0)
                    oncheck.append(1)
                else:
                    local = slave.index(temp[2])
                    ontimes[local] += 1
                    oncheck[local] = 1
            elif temp[1] == 'off':
                local = slave.index(temp[2])
                offtimes[local] += 1
                oncheck[local] = 0
            elif temp[1] == 'create':
                if temp[2] in slave:
                    local = slave.index(temp[2])
                    if oncheck[local] == 1:
                        offtimes[local] += 1
                        oncheck[local] = 0
    f.close()
    apcheck = []
    for i in range(len(slave)):
        apcheck.append(0)
    for i in range(len(time)):
        if tag[i] == 'aptq':
            temp = content[i].split(',')
            apcheck[slave.index(temp[0])] = 1
            if temp[0] not in mid:
                mid.append(temp[0])
                mid.append(message)
            local = mid.index(temp[0]) + 1
            mid[local][0] = time[i]
            mid[local][2] = temp[1]
            mid[local][3] = temp[2]

        elif tag[i] == 'rmfq':
            temp = content[i].split(',')
            apcheck[slave.index(temp[0])] = 0
            local = mid.index(temp[0]) + 1
            mid[local][1] = time[i]
            mid[local][7] = (mid[local][4] * 0.8 + mid[local][5] + mid[local][6] * 1.2) / 60
            information[slave.index(temp[0])].append(mid[local])
            mid[local] = initial()

        elif tag[i] == 'blowing':
            temp = content[i].split(',')
            local = mid.index(temp[0]) + 1
            if temp[1] == '1':
                mid[local][4] += 1
            elif temp[1] == '2':
                mid[local][5] += 1
            elif temp[1] == '3':
                mid[local][6] += 1

        elif tag[i] == 'createMaster':
            for j in range(len(apcheck)):
                if apcheck[j] != 0:
                    local = mid.index(slave[j]) + 1
                    mid[local][1] = time[i]
                    mid[local][7] = (mid[local][4] * 0.8 + mid[local][5] + mid[local][6] * 1.2) / 60
                    information[slave.index(temp[0])].append(mid[local])
                    mid[local] = initial()
                    apcheck[j] = 0

    for i in range(len(apcheck)):
        if apcheck[i] != 0:
            local = mid.index(slave[i]) + 1
            mid[local][1] = time[-1]
            mid[local][7] = (mid[local][4] * 0.8 + mid[local][5] + mid[local][6] * 1.2) / 60
            information[slave.index(temp[0])].append(mid[local])
            mid[local] = initial()
            apcheck[i] = 0

    tempreport = []
    for i in range(len(slave)):
        midreport = []
        midreport.append(slave[i])
        midreport.append(ontimes[i])
        midreport.append(offtimes[i])
        midreport.append(information[i])
        tempreport.append(midreport)

    cost = 0
    for i in range(len(tempreport)):
        for j in range(len(tempreport[i][-1])):
            cost += tempreport[i][-1][j][-1]
    report.append(tempreport)
    report.append(cost * 5)

    return report


# 获取从控机的信息
# [风量(能耗),费用]
def getMessage(slaveid):
    message = []
    report = getReport()
    mid = report[0]
    for i in range(len(mid)):
        if mid[i][0] == slaveid:
            temp = mid[i][3]
            power = 0
            cost = 0
            for j in range(len(temp)):
                power += temp[j][-1]
            cost = power * 5
            message.append(power)
            message.append(cost)
            break
    if len(message) == 0:
        message.append(0.0)
        message.append(0.0)
    return message
