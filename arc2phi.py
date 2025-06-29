from math import sin,cos,pi
from fractions import Fraction
import json
with open('chart.aff','r') as f: chart = f.readlines()
outChart = {'META':{'RPEVersion':150,'offset':int(chart[0][12:]),'name':None,'id':None,'song':None,'background':None,'background':None,'charter':None,'level':None},'BPMList':[{'startTime':[0,0,1],'bpm':120.0}],'judgeLineList':[{'numOfNotes':0,'isCover':1,'Texture':'line.png','eventLayers':[{'speedEvents':[],'moveXEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'moveYEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':-300.0,'end':-300.0,'easingType':1}],'rotateEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'alphaEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':255.0,'end':255.0,'easingType':1}]}],'notes':[],'Name':'Untitled','bpmfactor':1.0}]}
chart = chart[2:]
numOfNotes = 0
def note(typ,startTime,endTime,positionX,isFake,speed=1.0,size=1.0,alpha=255):
    global numOfNotes
    if not isFake: numOfNotes += 1
    return {'type':typ,'startTime':startTime,'endTime':endTime,'positionX':positionX,'above':1,'isFake':isFake,'speed':speed,'size':size,'yOffset':0.0,'visibleTime':999999.0,'alpha':alpha}
timingGroups = []
enwidenList = [(0,0)]
lines = []
timingGroupArg = None
cnt = 0
x = [-625.0,-375.0,-125.0,125.0,375.0,625.0]
scale = 500
def so(pos):
    return 1 - cos(pos * pi / 2)
def si(pos):
    return sin(pos * pi / 2)
def b(pos):
    return (1 - cos(pos * pi)) / 2
def RPETime(t):
    return [int(t),*Fraction(t%1).limit_denominator().as_integer_ratio()]
def adjustScale(t):
    global scale,x
    for enwiden,i in zip(enwidenList,range(len(enwidenList))):
        endTime = enwidenList[i+1][0] if i+1 < len(enwidenList) else 1e9
        if int(t) < enwiden[0]: break
        if int(t) > endTime: continue
        if enwiden[1]:
            scale = 400
            x = [-500,-300.0,-100.0,100.0,300.0,500.0]
        else:
            scale = 500
            x = [-625.0,-375.0,-125.0,125.0,375.0,625.0]
for line in chart:
    if 'enwiden' in line:
        t,enwidentype,mt,typ = line[15:-3].split(',')
        if enwidentype == 'enwidencamera': enwidenList.append((int(t),int(typ)))
    elif 'timinggroup' in line:
        timingGroupArg = line[12:-3]
        timingGroups.append((timingGroupArg,[]))
    elif timingGroupArg != None and '};' in line:
        timingGroupArg = None
        cnt += 1
    elif timingGroupArg != None: timingGroups[cnt][1].append(line[2:])
    else: lines.append(line)
BPMList = []
lastOffset = -1
for line in lines:
    if 'timing' in line:
        offset,BPM,beats = line[7:-3].split(',')
        if lastOffset == -1 and int(offset) != 0: outChart['judgeLineList'][0]['eventLayers'][0]['speedEvents'].append({'startTime':[0,0,1],'endTime':[0,0,1],'start':10.0,'end':10.0})
        if int(offset) != lastOffset: outChart['judgeLineList'][0]['eventLayers'][0]['speedEvents'].append({'startTime':RPETime(float(offset)/500),'endTime':RPETime(float(offset)/500),'start':float(BPM) / 20,'end':float(BPM) / 20})
        BPMList.append((int(offset),float(BPM)))
        lastOffset = int(offset)
for line in lines:
    if 'timing' in line: pass
    elif 'hold' in line:
        t1,t2,lane = line[5:-3].split(',')
        adjustScale(t1)
        outChart['judgeLineList'][0]['notes'].append(note(2,RPETime(float(t1)/500),RPETime(float(t2)/500),x[int(lane)],0))
        for time,i in zip(BPMList,range(len(BPMList))):
            endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
            if int(t1) < time[0]: break
            if int(t1) > endTime: continue
            BPM = time[1]
        if float(BPM) > 60000: BPM = 60000
        for time in range(int(t1),int(t2),int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
            adjustScale(time)
            if time != int(t1): outChart['judgeLineList'][0]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),x[int(lane)],1,10000.0))
    elif 'arc' in line:
        t1,t2,x1,x2,slideeasing,y1,y2,color,FX,skylineBoolean = line[4:line.index(')')].split(',')
        t1,t2 = int(t1),int(t2)
        if slideeasing == 's': progress = lambda time: (time-t1)/(t2-t1)
        elif slideeasing[:2] == 'si': progress = lambda time: si((time-t1)/(t2-t1))
        elif slideeasing[:2] == 'so': progress = lambda time: so((time-t1)/(t2-t1))
        elif slideeasing == 'b': progress = lambda time: b((time-t1)/(t2-t1))
        for time,i in zip(BPMList,range(len(BPMList))):
            endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
            if t1 < time[0]: break
            if t1 > endTime: continue
            BPM = time[1]
        if float(BPM) > 60000: BPM = 60000
        if skylineBoolean == 'false':
            for time in range(t1,t2,int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
                adjustScale(time)
                outChart['judgeLineList'][0]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,0,10000.0))
        f = False
        if t1 == t2:
            t2 += 5 if skylineBoolean == 'false' else 10
            r, f = range(t1,t2), True
        else: r = range(t1,t2,50) if skylineBoolean == 'false' else range(t1,t2,20)
        for time in r:
            adjustScale(time)
            if skylineBoolean == 'false': outChart['judgeLineList'][0]['notes'].append(note(4,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,1))
            elif 'designant' in line: outChart['judgeLineList'][0]['notes'].append(note(3,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,1,size=0.1,alpha=128))
            else: outChart['judgeLineList'][0]['notes'].append(note(2,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500+0.01),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,1,size=0.1,alpha=128))
        if '[' in line:
            for arctap in line[line.index('[')+1:line.index(']')].split(','):
                adjustScale(arctap[7:-1])
                if 'designant' in line: outChart['judgeLineList'][0]['notes'].append(note(3,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale,1))
                outChart['judgeLineList'][0]['notes'].append(note(1,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale,0))
    elif 'scenecontrol' in line: pass
    elif 'camera' in line: pass
    else:
        t1,lane = line[1:-3].split(',')
        adjustScale(t1)
        outChart['judgeLineList'][0]['notes'].append(note(1,RPETime(float(t1)/500),RPETime(float(t1)/500),x[int(lane)],0))
    outChart['judgeLineList'][0]['numOfNotes'] = numOfNotes
cnt = 1
for timingGroup in timingGroups:
    outChart['judgeLineList'].append({'numOfNotes':0,'isCover':1,'Texture':'line.png','eventLayers':[{'speedEvents':[],'moveXEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'moveYEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':-300.0,'end':-300.0,'easingType':1}],'rotateEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'alphaEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':255.0,'end':255.0,'easingType':1}]}],'notes':[],'Name':'Untitled','bpmfactor':1.0})
    numOfNotes = 0
    BPMList = []
    lastOffset = -1
    for line in timingGroup[1]:
        if 'timing' in line:
            offset,BPM,beats = line[7:-3].split(',')
            if lastOffset == -1 and int(offset) != 0: outChart['judgeLineList'][cnt]['eventLayers'][0]['speedEvents'].append({'startTime':[0,0,1],'endTime':[0,0,1],'start':10.0,'end':10.0})
            if int(offset) != lastOffset: outChart['judgeLineList'][cnt]['eventLayers'][0]['speedEvents'].append({'startTime':RPETime(float(offset)/500),'endTime':RPETime(float(offset)/500),'start':float(BPM) / 20,'end':float(BPM) / 20})
            BPMList.append((int(offset),float(BPM)))
            lastOffset = int(offset)
    for line in timingGroup[1]:
        if 'timing' in line: pass
        elif 'hold' in line:
            t1,t2,lane = line[5:-3].split(',')
            adjustScale(t1)
            outChart['judgeLineList'][cnt]['notes'].append(note(2,RPETime(float(t1)/500),RPETime(float(t2)/500),x[int(lane)],(1 if timingGroup[0] == 'noinput' else 0)))
            for time,i in zip(BPMList,range(len(BPMList))):
                endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
                if int(t1) < time[0]: break
                if int(t1) > endTime: continue
                BPM = time[1]
            if float(BPM) > 60000: BPM = 60000
            for time in range(int(t1),int(t2),int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
                adjustScale(time)
                if time != int(t1): outChart['judgeLineList'][cnt]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),x[int(lane)],(1 if timingGroup[0] == 'noinput' else 0),10000.0))
        elif 'arc' in line:
            t1,t2,x1,x2,slideeasing,y1,y2,color,FX,skylineBoolean = line[4:line.index(')')].split(',')
            t1,t2 = int(t1),int(t2)
            if slideeasing == 's': progress = lambda time: (time-t1)/(t2-t1)
            elif slideeasing[:2] == 'si': progress = lambda time: si((time-t1)/(t2-t1))
            elif slideeasing[:2] == 'so': progress = lambda time: so((time-t1)/(t2-t1))
            elif slideeasing == 'b': progress = lambda time: b((time-t1)/(t2-t1))
            for time,i in zip(BPMList,range(len(BPMList))):
                endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
                if t1 < time[0]: break
                if t1 > endTime: continue
                BPM = time[1]
            if float(BPM) > 60000: BPM = 60000
            if skylineBoolean == 'false':
                for time in range(t1,t2,int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
                    adjustScale(time)
                    outChart['judgeLineList'][cnt]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,(1 if timingGroup[0] == 'noinput' else 0),10000.0))
            f = False
            if t1 == t2:
                t2 += 5 if skylineBoolean == 'false' else 10
                r, f = range(t1,t2), True
            else: r = range(t1,t2,50) if skylineBoolean == 'false' else range(t1,t2,20)
            for time in r:
                adjustScale(time)
                if skylineBoolean == 'false': outChart['judgeLineList'][cnt]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,1))
                elif 'designant' in line: outChart['judgeLineList'][cnt]['notes'].append(note(3,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,1,size=0.1,alpha=128))
                else: outChart['judgeLineList'][cnt]['notes'].append(note(2,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500+0.01),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale,1,size=0.1,alpha=128))
            if '[' in line:
                for arctap in line[line.index('[')+1:line.index(']')].split(','):
                    adjustScale(arctap[7:-1])
                    if 'designant' in line: outChart['judgeLineList'][cnt]['notes'].append(note(3,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(int(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale,1))
                    outChart['judgeLineList'][cnt]['notes'].append(note(1,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(int(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale,(1 if timingGroup[0] == 'noinput' else 0)))
        elif 'scenecontrol' in line:
            if 'hidegroup' in line:
                t,hidegroup,x,typ = line[13:-3].split(',')
                outChart['judgeLineList'][cnt]['eventLayers'][0]['moveYEvents'].append({'startTime':RPETime(float(t)/500),'endTime':RPETime(float(t)/500),'start':(-300 if not int(typ) else 1000),'end':(-300 if not int(typ) else 1000),'easingType':1})
        elif 'camera' in line: pass
        else:
            t1,lane = line[1:-3].split(',')
            adjustScale(t1)
            outChart['judgeLineList'][cnt]['notes'].append(note(1,RPETime(float(t1)/500),RPETime(float(t1)/500),x[int(lane)],(1 if timingGroup[0] == 'noinput' else 0)))
    cnt += 1
with open('chart.json','w') as f: f.write(json.dumps(outChart))