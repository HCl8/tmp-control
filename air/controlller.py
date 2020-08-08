from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
import air.staticVar as static
from slaveMachine import SlaveMachine
from masterMachine import MasterMachine
from django.http import HttpResponse
import report
import time
import json


def logonF(request):
    return render(request, 'logon.html', {})


def masterF(request):
    context = {}
    return render(request, 'masterMachine.html', context)


def slaveF(request):
    context = {}
    if 'roomid' in request.POST:
        if request.POST['roomid'] in static.roomidTable:
            if request.POST['idcard'] == static.roomidTable[request.POST['roomid']]:
                static.master.createSlave(request.POST['roomid'])
                return render(request, 'slaveMachine.html', {'roomid': request.POST['roomid']})
        context['error'] = "输入信息有误！"
        return render(request, 'logon.html', context)


def slaveApi(request: WSGIRequest):
    roomid = request.headers['roomid']
    slave: SlaveMachine = static.master.slaves[roomid]
    if 'power' in request.headers:
        if request.headers['power'] == 'on':
            slave.on()
        else:
            slave.off()
    if 'blowing' in request.headers:
        slave.setSpeed(int(request.headers['blowing']))
    if 'temp' in request.headers:
        slave.setTargetTemp(int(request.headers['temp']))
    if 'alive' in request.headers:
        slave.alive = time.time()
    message = {}
    message['isWork'] = slave.working
    message['targetTemp'] = slave.targetTemp
    message['nowTemp'] = slave.nowTemp
    message['mode'] = slave.mode
    message['isB'] = slave.isblowing
    cost = report.getMessage(slave.id)
    message['Bspeed'] = trans(slave.speed)
    message['cost'] = f'{cost[1]:.2f}'
    message['energy'] = f'{cost[0]:.2f}'
    return HttpResponse(json.dumps(message))


def trans(self):
    if self.value == 1:
        return 'LOW'
    elif self.value == 2:
        return 'MIDDLE'
    else:
        return 'HIGH'


def masterApi(request: WSGIRequest):
    master: MasterMachine = static.master

    if 'temp' in request.headers:
        master.targetTemp = int(request.headers['temp'])
    if 'mode' in request.headers:
        master.setMode(request.headers['mode'])
    if 'power' in request.headers:
        if request.headers['power'] == 'on':
            master.on()
        else:
            master.off()
    message = {}
    message['isWork'] = master.working
    message['targetTemp'] = master.targetTemp
    message['mode'] = master.mode
    message['stat'] = master.mode
    return HttpResponse(json.dumps(message))


def allSlaves(request):
    slave: SlaveMachine
    result = []
    for slave in static.master.slaves.values():
        result.append(
            [
                slave.id,
                slave.connecting,
                slave.working,
                slave.nowTemp,
                slave.isblowing,
                trans(slave.speed)
            ]
        )
    return HttpResponse(json.dumps(result))


def list(request):
    data = []
    message = report.getReport()
    for i in range(0, len(message[0])):
        data.append([
            message[0][i][0], message[0][i][1], message[0][i][2]
        ])
        for j in message[0][i][3]:
            data.append(j.copy())
    for j in data:
        if len(j) == 8:
            j[7] = f"{j[7]:.3f}"
    return render(request, 'list.html', {'data': data,'cost':f"{message[1]:.3f}"})
