from math import sin,cos,pi
from fractions import Fraction
import json
with open('chart.aff','r') as f: chart = f.readlines()
outChart = {'META':{'RPEVersion':150,'offset':int(chart[0][12:]),'name':None,'id':None,'song':None,'background':None,'background':None,'charter':None,'level':None},'BPMList':[{'startTime':[0,0,1],'bpm':120.0}],'judgeLineList':[]}
for y in reversed(range(0,301,10)):
    outChart['judgeLineList'].append({'numOfNotes':0,'isCover':1,'Texture':'line.png','eventLayers':[{'speedEvents':[],'moveXEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'moveYEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':-y,'end':-y,'easingType':1}],'rotateEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'alphaEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':255.0 if y == 0 or y == 300 else 0,'end':255.0 if y == 0 or y == 300 else 0,'easingType':1}]}],'posControl':[{'easing': 1,'pos':1.0,'x':0.0},{'easing':1,'pos':1.0,'x':9999999.0}],'sizeControl':[{'easing':1,'size':1.0,'x':0.0},{'easing':1,'size':1.0,'x':9999999.0}],'yControl':[{'easing':1,'x':0.0,'y':1.0},{'easing':1,'x':9999999.0,'y':1.0}],'notes':[],'Name':'Untitled','bpmfactor':1.0})
    for i in range(26):
        s = 1/(1+(8+(1-y/300)*8)*(i/25))
        outChart['judgeLineList'][int(30-y/10)]['posControl'].insert(-1,{"easing": 1, "x": i*120, "pos": s})
        outChart['judgeLineList'][int(30-y/10)]['sizeControl'].insert(-1,{"easing": 1, "x": i*120, "size": s})
        outChart['judgeLineList'][int(30-y/10)]['yControl'].insert(-1,{"easing": 1, "x": i*120, "y": s})
chart = chart[2:]
def note(typ,startTime,endTime,positionX,isFake,speed=1.0,size=1.0,visibleTime=999999.0,alpha=255):
    return {'type':typ,'startTime':startTime,'endTime':endTime,'positionX':positionX,'above':1,'isFake':isFake,'speed':speed,'size':size,'yOffset':0.0,'visibleTime':visibleTime,'alpha':alpha}
timingGroups = []
enwidenList = [(0,0)]
lines = []
timingGroupArg = None
cnt = 0
x = [-625.0,-375.0,-125.0,125.0,375.0,625.0]
scaleX = 500
scaleY = 1
def so(pos):
    return 1 - cos(pos * pi / 2)
def si(pos):
    return sin(pos * pi / 2)
def b(pos):
    return (1 - cos(pos * pi)) / 2
def RPETime(t):
    return [int(t),*Fraction(t%1).limit_denominator().as_integer_ratio()]
def adjustScale(t):
    global scaleX,scaleY,x
    for enwiden,i in zip(enwidenList,range(len(enwidenList))):
        endTime = enwidenList[i+1][0] if i+1 < len(enwidenList) else 1e9
        if int(t) < enwiden[0]: break
        if int(t) > endTime: continue
        if enwiden[1]:
            scaleX = 400
            scaleY = 1.61
            x = [-500,-300.0,-100.0,100.0,300.0,500.0]
        else:
            scaleX = 500
            scaleY = 1
            x = [-625.0,-375.0,-125.0,125.0,375.0,625.0]
def find(t,lineId=None):
    global BPMList
    if lineId == None:
        if float(t) < BPMList[0][0]:
            start, BPM, floorPos = BPMList[0]
            return start, min(BPM, 60000), floorPos
        for time,i in zip(BPMList,range(len(BPMList))):
            endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
            if time[0] <= float(t) < endTime: return time[0],min(time[1],60000),time[2]
        start, BPM, floorPos = BPMList[-1]
        return start, min(BPM, 60000), floorPos
    else:
        if float(t) < BPMList[0][2][lineId]:
            start, BPM, floorPos = BPMList[0]
            return start, min(BPM, 60000), floorPos
        for time,i in zip(BPMList,range(len(BPMList))):
            endPos = BPMList[i+1][2][lineId] if i+1 < len(BPMList) else 1e9
            if time[2][lineId] <= float(t) < endPos: return time[0],min(time[1],60000),time[2]
        start, BPM, floorPos = BPMList[-1]
        return start, min(BPM, 60000), floorPos
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
lastOffset = None
lastBPM = 200
floorPos = [0]*31
for line in lines:
    if 'timing' in line:
        offset,BPM,beats = line[7:-3].split(',')
        if lastOffset == None:
            if int(offset) != 0:
                for i in range(31): outChart['judgeLineList'][i]['eventLayers'][0]['speedEvents'].append({'startTime':[0,0,1],'endTime':[0,0,1],'start':lastBPM/15*(1-i/90)*1.8,'end':lastBPM/15*(1-i/90)*1.8})
                BPMList.append((0,lastBPM,floorPos.copy()))
            lastOffset = 0
        else:
            for i in range(31): floorPos[i] += (float(offset)-(lastOffset or 0))*(lastBPM/15*(1-i/90)*1.8*120)
            for i in range(31): outChart['judgeLineList'][i]['eventLayers'][0]['speedEvents'].append({'startTime':RPETime(float(offset)/500),'endTime':RPETime(float(offset)/500),'start':float(BPM)/15*(1-i/90)*1.8,'end':float(BPM)/15*(1-i/90)*1.8})
        BPMList.append((int(offset),float(BPM),floorPos.copy()))
        lastOffset = int(offset)
        lastBPM = float(BPM)
for line in lines:
    if 'timing' in line: pass
    elif 'hold' in line:
        t1,t2,lane = line[5:-3].split(',')
        adjustScale(t1)
        start1,BPM1,floorPos1 = find(t1)
        pos = floorPos1[0]+(float(t1)-start1)*(BPM1/15*1.8*120)+3000
        start2,BPM2,floorPos2 = find(pos,lineId=0)
        outChart['judgeLineList'][0]['notes'].append(note(1,RPETime(float(t1)/500),RPETime(float(t1)/500),x[int(lane)],0,visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-float(t1)))
        for time in range(int(t1),int(t2),50):
            adjustScale(time)
            start1,BPM1,floorPos1 = find(time)
            pos = floorPos1[0]+(time-start1)*(BPM1/15*1.8*120)+3000
            start2,BPM2,floorPos2 = find(pos,lineId=0)
            if time != int(t1): outChart['judgeLineList'][0]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),x[int(lane)],1,visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-time))
        time = float(t1)
        while time < float(t2):
            adjustScale(time)
            start1,BPM1,floorPos1 = find(time)
            pos = floorPos1[0]+(time-start1)*(BPM1/15*1.8*120)+3000
            start2,BPM2,floorPos2 = find(pos,lineId=0)
            step = int((30000 if BPM1 < 255 else 60000) / BPM1)
            if time != int(t1): outChart['judgeLineList'][0]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),x[int(lane)],1,10000.0,visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-time))
            time += step
    elif 'arc' in line:
        t1,t2,x1,x2,slideeasing,y1,y2,color,FX,skylineBoolean = line[4:line.index(')')].split(',')
        t1,t2 = int(t1),int(t2)
        if slideeasing == 's': progress = lambda time: (time-t1)/(t2-t1)
        elif slideeasing[:2] == 'si': progress = lambda time: si((time-t1)/(t2-t1))
        elif slideeasing[:2] == 'so': progress = lambda time: so((time-t1)/(t2-t1))
        elif slideeasing == 'b': progress = lambda time: b((time-t1)/(t2-t1))
        if skylineBoolean == 'false':
            time = t1
            while time < t2:
                adjustScale(time)
                start1,BPM1,floorPos1 = find(time)
                lineId = max(0,min(round((float(y1)+progress(time)*(float(y2)-float(y1)))/scaleY*30),30))
                pos = floorPos1[lineId]+(time-start1)*(BPM1/15*(1-lineId/90)*1.8*120)+3000
                start2,BPM2,floorPos2 = find(pos,lineId=lineId)
                step = int((30000 if BPM1 < 255 else 60000) / BPM1)
                outChart['judgeLineList'][lineId]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,0,10000.0,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-time))
                time += step
        f = False
        if t1 == t2:
            t2 += 5 if skylineBoolean == 'false' else 10
            r, f = range(t1,t2), True
        else: r = range(t1,t2,50) if skylineBoolean == 'false' else range(t1,t2,20)
        for time in r:
            adjustScale(t1 if f else time)
            lineId = max(0,min(round((float(y1)+progress(time)*(float(y2)-float(y1)))/scaleY*30),30))
            start1,BPM1,floorPos1 = find(t1 if f else time)
            pos = floorPos1[lineId]+((t1 if f else time)-start1)*(BPM1/15*(1-lineId/90)*1.8*120)+3000
            start2,BPM2,floorPos2 = find(pos,lineId=lineId)
            if skylineBoolean == 'false': outChart['judgeLineList'][lineId]['notes'].append(note(4,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-(t1 if f else time)))
            elif 'designant' in line: outChart['judgeLineList'][lineId]['notes'].append(note(3,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,1,size=0.1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-(t1 if f else time),alpha=128))
            else: outChart['judgeLineList'][lineId]['notes'].append(note(2,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500+0.01),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,1,size=0.1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-(t1 if f else time),alpha=128))
        if '[' in line:
            for arctap in line[line.index('[')+1:line.index(']')].split(','):
                adjustScale(arctap[7:-1])
                lineId = max(0,min(round((float(y1)+progress(float(arctap[7:-1]))*(float(y2)-float(y1)))/scaleY*30),30))
                start1,BPM1,floorPos1 = find(arctap[7:-1])
                pos = floorPos1[lineId]+(float(arctap[7:-1])-start1)*(BPM1/15*(1-lineId/90)*1.8*120)+3000
                start2,BPM2,floorPos2 = find(pos,lineId=lineId)
                if 'designant' in line: outChart['judgeLineList'][lineId]['notes'].append(note(3,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scaleX,1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-float(arctap[7:-1])))
                outChart['judgeLineList'][lineId]['notes'].append(note(1,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scaleX,0,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-float(arctap[7:-1])))
    elif 'scenecontrol' in line: pass
    elif 'camera' in line: pass
    else:
        t1,lane = line[1:-3].split(',')
        adjustScale(t1)
        start1,BPM1,floorPos1 = find(t1)
        pos = floorPos1[0]+(float(t1)-start1)*(BPM1/15*1.8*120)+3000
        start2,BPM2,floorPos2 = find(pos,lineId=0)
        outChart['judgeLineList'][0]['notes'].append(note(1,RPETime(float(t1)/500),RPETime(float(t1)/500),x[int(lane)],0,visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-float(t1)))
    for line in outChart['judgeLineList']:
        numOfNotes = 0
        for n in line['notes']:
            if not n['isFake']: numOfNotes += 1
        line['numOfNotes'] = numOfNotes
cnt = 31
for timingGroup in timingGroups:
    for y in reversed(range(0,301,10)):
        outChart['judgeLineList'].append({'numOfNotes':0,'isCover':1,'Texture':'line.png','eventLayers':[{'speedEvents':[],'moveXEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'moveYEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':-y,'end':-y,'easingType':1}],'rotateEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}],'alphaEvents':[{'startTime':[0,0,1],'endTime':[0,0,1],'start':0.0,'end':0.0,'easingType':1}]}],'posControl':[{'easing': 1,'pos':1.0,'x':0.0},{'easing':1,'pos':1.0,'x':9999999.0}],'sizeControl':[{'easing':1,'size':1.0,'x':0.0},{'easing':1,'size':1.0,'x':9999999.0}],'yControl':[{'easing':1,'x':0.0,'y':1.0},{'easing':1,'x':9999999.0,'y':1.0}],'notes':[],'Name':'Untitled','bpmfactor':1.0})
        for i in range(26):
            s = 1/(1+(8+(1-y/300)*8)*(i/25))
            outChart['judgeLineList'][cnt+int(30-y/10)]['posControl'].insert(-1,{"easing": 1, "x": i*120, "pos": s})
            outChart['judgeLineList'][cnt+int(30-y/10)]['sizeControl'].insert(-1,{"easing": 1, "x": i*120, "size": s})
            outChart['judgeLineList'][cnt+int(30-y/10)]['yControl'].insert(-1,{"easing": 1, "x": i*120, "y": s})
    BPMList = []
    lastOffset = None
    lastBPM = 200
    floorPos = [0]*31
    for line in timingGroup[1]:
        if 'timing' in line:
            offset,BPM,beats = line[7:-3].split(',')
            if lastOffset == None:
                if int(offset) != 0:
                    for i in range(31): outChart['judgeLineList'][cnt+i]['eventLayers'][0]['speedEvents'].append({'startTime':[0,0,1],'endTime':[0,0,1],'start':lastBPM/15*(1-i/90)*1.8,'end':lastBPM/15*(1-i/90)*1.8})
                    BPMList.append((0,200,floorPos.copy()))
                lastOffset = 0
            for i in range(31): floorPos[i] += (float(offset)-(lastOffset or 0))*(lastBPM/15*(1-i/90)*1.8*120)
            for i in range(31): outChart['judgeLineList'][cnt+i]['eventLayers'][0]['speedEvents'].append({'startTime':RPETime(float(offset)/500),'endTime':RPETime(float(offset)/500),'start':float(BPM)/15*(1-i/90)*1.8,'end':float(BPM)/15*(1-i/90)*1.8})
            BPMList.append((int(offset),float(BPM),floorPos.copy()))
            lastOffset = int(offset)
            lastBPM = float(BPM)
    for line in timingGroup[1]:
        if 'timing' in line: pass
        elif 'hold' in line:
            t1,t2,lane = line[5:-3].split(',')
            adjustScale(t1)
            start1,BPM1,floorPos1 = find(t1)
            pos = floorPos1[0]+(float(t1)-start1)*(BPM1/15*1.8*120)+3000
            start2,BPM2,floorPos2 = find(pos,lineId=0)
            outChart['judgeLineList'][cnt]['notes'].append(note(1,RPETime(float(t1)/500),RPETime(float(t1)/500),x[int(lane)],(1 if timingGroup[0] == 'noinput' else 0),visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-float(t1)))
            for time in range(int(t1),int(t2),50):
                adjustScale(time)
                start1,BPM1,floorPos1 = find(time)
                pos = floorPos1[0]+(time-start1)*(BPM1/15*1.8*120)+3000
                start2,BPM2,floorPos2 = find(pos,lineId=0)
                if time != int(t1): outChart['judgeLineList'][cnt]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),x[int(lane)],1,visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-time))
            time = float(t1)
            while time < float(t2):
                adjustScale(time)
                start1,BPM1,floorPos1 = find(time)
                pos = floorPos1[0]+(time-start1)*(BPM1/15*1.8*120)+3000
                start2,BPM2,floorPos2 = find(pos,lineId=0)
                step = int((30000 if BPM1 < 255 else 60000) / BPM1)
                if time != int(t1): outChart['judgeLineList'][cnt]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),x[int(lane)],(1 if timingGroup[0] == 'noinput' else 0),10000.0,visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-time))
                time += step
        elif 'arc' in line:
            t1,t2,x1,x2,slideeasing,y1,y2,color,FX,skylineBoolean = line[4:line.index(')')].split(',')
            t1,t2 = int(t1),int(t2)
            if slideeasing == 's': progress = lambda time: (time-t1)/(t2-t1)
            elif slideeasing[:2] == 'si': progress = lambda time: si((time-t1)/(t2-t1))
            elif slideeasing[:2] == 'so': progress = lambda time: so((time-t1)/(t2-t1))
            elif slideeasing == 'b': progress = lambda time: b((time-t1)/(t2-t1))
            if skylineBoolean == 'false':
                time = t1
                while time < t2:
                    adjustScale(time)
                    start1,BPM1,floorPos1 = find(time)
                    lineId = max(0,min(round((float(y1)+progress(time)*(float(y2)-float(y1)))/scaleY*30),30))
                    pos = floorPos1[lineId]+(time-start1)*(BPM1/15*(1-lineId/90)*1.8*120)+3000
                    start2,BPM2,floorPos2 = find(pos,lineId=lineId)
                    step = int((30000 if BPM1 < 255 else 60000) / BPM1)
                    outChart['judgeLineList'][cnt+lineId]['notes'].append(note(4,RPETime(time/500),RPETime(time/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,(1 if timingGroup[0] == 'noinput' else 0),10000.0,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-time))
                    time += step
            f = False
            if t1 == t2:
                t2 += 5 if skylineBoolean == 'false' else 10
                r, f = range(t1,t2), True
            else: r = range(t1,t2,50) if skylineBoolean == 'false' else range(t1,t2,20)
            for time in r:
                adjustScale(t1 if f else time)
                lineId = max(0,min(round((float(y1)+progress(time)*(float(y2)-float(y1)))/scaleY*30),30))
                start1,BPM1,floorPos1 = find(t1 if f else time)
                pos = floorPos1[lineId]+((t1 if f else time)-start1)*(BPM1/15*(1-lineId/90)*1.8*120)+3000
                start2,BPM2,floorPos2 = find(pos,lineId=lineId)
                if skylineBoolean == 'false': outChart['judgeLineList'][cnt+lineId]['notes'].append(note(4,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-(t1 if f else time)))
                elif 'designant' in line: outChart['judgeLineList'][cnt+lineId]['notes'].append(note(3,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,1,size=0.1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-(t1 if f else time),alpha=128))
                else: outChart['judgeLineList'][cnt+lineId]['notes'].append(note(2,RPETime((t1 if f else time)/500),RPETime((t1 if f else time)/500+0.01),(float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scaleX,1,size=0.1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-(t1 if f else time),alpha=128))
            if '[' in line:
                for arctap in line[line.index('[')+1:line.index(']')].split(','):
                    adjustScale(arctap[7:-1])
                    lineId = max(0,min(round((float(y1)+progress(float(arctap[7:-1]))*(float(y2)-float(y1)))/scaleY*30),30))
                    start1,BPM1,floorPos1 = find(arctap[7:-1])
                    pos = floorPos1[lineId]+(float(arctap[7:-1])-start1)*(BPM1/15*(1-lineId/90)*1.8*120)+3000
                    start2,BPM2,floorPos2 = find(pos,lineId=lineId)
                    if 'designant' in line: outChart['judgeLineList'][cnt+lineId]['notes'].append(note(3,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scaleX,1,visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-float(arctap[7:-1])))
                    outChart['judgeLineList'][cnt+lineId]['notes'].append(note(1,RPETime(float(arctap[7:-1])/500),RPETime(float(arctap[7:-1])/500),(float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scaleX,(1 if timingGroup[0] == 'noinput' else 0),visibleTime=start2+(pos-floorPos2[lineId])/(BPM2/15*(1-lineId/90)*1.8*120)-float(arctap[7:-1])))
        elif 'scenecontrol' in line:
            if 'hidegroup' in line:
                t,hidegroup,x,typ = line[13:-3].split(',')
                for i in range(31): outChart['judgeLineList'][cnt+i]['eventLayers'][0]['moveYEvents'].append({'startTime':RPETime(float(t)/500),'endTime':RPETime(float(t)/500),'start':(10*(i-30) if not int(typ) else 1000),'end':(10*(i-30) if not int(typ) else 1000),'easingType':1})
        elif 'camera' in line: pass
        else:
            t1,lane = line[1:-3].split(',')
            adjustScale(t1)
            start1,BPM1,floorPos1 = find(t1)
            pos = floorPos1[0]+(float(t1)-start1)*(BPM1/15*1.8*120)+3000
            start2,BPM2,floorPos2 = find(pos,lineId=0)
            outChart['judgeLineList'][cnt]['notes'].append(note(1,RPETime(float(t1)/500),RPETime(float(t1)/500),x[int(lane)],(1 if timingGroup[0] == 'noinput' else 0),visibleTime=start2+(pos-floorPos2[0])/(BPM2/15*1.8*120)-float(t1)))
    cnt += 31
with open('chart.json','w') as f: f.write(json.dumps(outChart))