from math import sin,cos,pi
with open('chart.aff','r') as f: chart = f.readlines()
outChart = str(int(chart[0][12:])+175) + '\nbp 0.0 120.0\ncp 0 0.0 1024.0 300.0\nca 0 0.0 255\ncd 0 0.0 0.0\n'
chart = chart[2:]
timingGroups = []
enwidenList = [(0,0)]
lines = []
timingGroupArg = None
cnt = 0
x = ['-1000.0','-600.0','-200.0','200.0','600.0','1000.0']
scale = 600
def si(pos):
    return 1 - cos(pos * pi / 2)
def so(pos):
    return sin(pos * pi / 2)
def b(pos):
    return (1 - cos(pos * pi)) / 2
def adjustScale(t):
    global scale,x
    for enwiden,i in zip(enwidenList,range(len(enwidenList))):
        endTime = enwidenList[i+1][0] if i+1 < len(enwidenList) else 1e9
        if int(t) < enwiden[0]: break
        if int(t) > endTime: continue
        if enwiden[1]:
            scale = 375
            x = ['-750','-450','-150','150','450','750']
        else:
            scale = 600
            x = ['-1000','-600','-200','200','600','1000']
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
        if lastOffset == -1 and int(offset) != 0: outChart += 'cv 0 0.0 10.0\n'
        if int(offset) != lastOffset: outChart += 'cv 0 ' + str(float(offset)/500) + ' ' + str(float(BPM) / 12) + '\n'       
        BPMList.append((int(offset),float(BPM)))
        lastOffset = int(offset)
for line in lines:
    if 'timing' in line: pass
    elif 'hold' in line:
        t1,t2,lane = line[5:-3].split(',')
        adjustScale(t1)
        outChart += 'n2 0 ' + str(float(t1)/500) + ' ' + str(float(t2)/500) + ' ' + x[int(lane)] + ' 1 0\n# 1.0\n& 1.0\n'
        for time,i in zip(BPMList,range(len(BPMList))):
            endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
            if int(t1) < time[0]: break
            if int(t1) > endTime: continue
            BPM = time[1]
        if float(BPM) > 60000: BPM = 60000
        for time in range(int(t1),int(t2),int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
            adjustScale(time)
            outChart += 'n4 0 ' + str(time/500) + ' ' + x[int(lane)] + ' 1 0\n# 10000.0\n& 1.0\n'
    elif 'arc' in line:
        t1,t2,x1,x2,slideeasing,y1,y2,color,FX,skylineBoolean = line[4:line.index(')')].split(',')
        t1,t2 = int(t1),int(t2)
        if slideeasing == 's': progress = lambda time: (time-t1)/(t2-t1)
        elif slideeasing[:2] == 'si': progress = lambda time: si((time-t1)/(t2-t1))
        elif slideeasing[:2] == 'so': progress = lambda time: so((time-t1)/(t2-t1))
        elif slideeasing == 'b': progress = lambda time: b((time-t1)/(t2-t1))
        if skylineBoolean == 'false':
            for time,i in zip(BPMList,range(len(BPMList))):
                endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
                if t1 < time[0]: break
                if t1 > endTime: continue
                BPM = time[1]
            if float(BPM) > 60000: BPM = 60000
            for time in range(t1,t2,int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
                adjustScale(time)
                outChart += 'n4 0 ' + str(time/500) + ' ' + str((float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale) + ' 1 0\n# 10000.0\n& 1.0\n'
            f = False
            if t1 == t2:
                t2 += 5
                r, f = range(t1,t2), True
            else: r = range(t1,t2,50)
            for time in r:
                adjustScale(time)
                outChart += 'n4 0 ' + str((t1 if f else time)/500) + ' ' + str((float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale) + ' 1 1\n# 1.0\n& 1.0\n'
        if '[' in line:
            for arctap in line[line.index('[')+1:line.index(']')].split(','):
                adjustScale(arctap[7:-1])
                if 'designant' in line: outChart += 'n3 0 ' + str(float(arctap[7:-1])/500) + ' ' + str((float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale) + ' 1 1\n# 1.0\n& 1.0\n'
                outChart += 'n1 0 ' + str(float(arctap[7:-1])/500) + ' ' + str((float(x1)+progress(float(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale) + ' 1 0\n# 1.0\n& 1.0\n'
    elif 'scenecontrol' in line: pass
    elif 'camera' in line: pass
    else:
        t1,lane = line[1:-3].split(',')
        adjustScale(t1)
        outChart += 'n1 0 ' + str(float(t1)/500) + ' ' + x[int(lane)] + ' 1 0\n# 1.0\n& 1.0\n'
cnt = 1
for timingGroup in timingGroups:
    judgeLine = 'cp ' + str(cnt) + ' 0.0 1024.0 300.0\nca ' + str(cnt) + ' 0.0 255\ncd ' + str(cnt) + ' 0.0 0.0\n'
    BPMList = []
    lastOffset = -1
    for line in timingGroup[1]:
        if 'timing' in line:
            offset,BPM,beats = line[7:-3].split(',')
            if lastOffset == -1 and int(offset) != 0: outChart += 'cv ' + str(cnt) + ' 0.0 10.0\n'
            if int(offset) != lastOffset: judgeLine += 'cv ' + str(cnt) + ' ' + str(float(offset)/500) + ' ' + str(float(BPM) / 12) + '\n'
            BPMList.append((int(offset),float(BPM)))
            lastOffset = int(offset)
    for line in timingGroup[1]:
        if 'timing' in line: pass
        elif 'hold' in line:
            t1,t2,lane = line[5:-3].split(',')
            adjustScale(t1)
            judgeLine += 'n2 ' + str(cnt) + ' ' + str(float(t1)/500) + ' ' + str(float(t2)/500) + ' ' + x[int(lane)] + ' 1 ' + ('1\n# 1.0\n& 1.0\n' if timingGroup[0] == 'noinput' else '0\n# 1.0\n& 1.0\n')
            for time,i in zip(BPMList,range(len(BPMList))):
                endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
                if int(t1) < time[0]: break
                if int(t1) > endTime: continue
                BPM = time[1]
            if float(BPM) > 60000: BPM = 60000
            for time in range(int(t1),int(t2),int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
                adjustScale(time)
                judgeLine += 'n4 ' + str(cnt) + ' ' + str(time/500) + ' ' + x[int(lane)] + (' 1 1\n# 10000.0\n& 1.0\n' if timingGroup[0] == 'noinput' else ' 1 0\n# 10000.0\n& 1.0\n')
        elif 'arc' in line:
            t1,t2,x1,x2,slideeasing,y1,y2,color,FX,skylineBoolean = line[4:line.index(')')].split(',')
            t1,t2 = int(t1),int(t2)
            if slideeasing == 's': progress = lambda time: (time-t1)/(t2-t1)
            elif slideeasing[:2] == 'si': progress = lambda time: si((time-t1)/(t2-t1))
            elif slideeasing[:2] == 'so': progress = lambda time: so((time-t1)/(t2-t1))
            elif slideeasing == 'b': progress = lambda time: b((time-t1)/(t2-t1))
            if skylineBoolean == 'false':
                for time,i in zip(BPMList,range(len(BPMList))):
                    endTime = BPMList[i+1][0] if i+1 < len(BPMList) else 1e9
                    if t1 < time[0]: break
                    if t1 > endTime: continue
                    BPM = time[1]
                if float(BPM) > 60000: BPM = 60000
                for time in range(t1,t2,int((30000 if float(BPM) < 255 else 60000)/float(BPM))):
                    adjustScale(time)
                    judgeLine += 'n4 ' + str(cnt) + ' ' + str(time/500) + ' ' + str((float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale) + ' 1 ' + ('1\n# 10000.0\n& 1.0\n' if timingGroup[0] == 'noinput' else '0\n# 10000.0\n& 1.0\n')
                f = False
                if t1 == t2:
                    t2 += 5
                    r, f = range(t1,t2), True
                else: r = range(t1,t2,50)
                for time in r:
                    adjustScale(time)
                    judgeLine += 'n4 ' + str(cnt) + ' ' + str((t1 if f else time)/500) + ' ' + str((float(x1)+progress(time)*(float(x2)-float(x1))-0.5)*scale) + ' 1 1\n# 1.0\n& 1.0\n'
            if '[' in line:
                for arctap in line[line.index('[')+1:line.index(']')].split(','):
                    adjustScale(arctap[7:-1])
                    if 'designant' in line: judgeLine += 'n3 ' + str(cnt) + ' ' + str(float(arctap[7:-1])/500) + ' ' + str((float(x1)+progress(int(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale) + ' 1 1\n# 1.0\n& 1.0\n'
                    judgeLine += 'n1 ' + str(cnt) + ' ' + str(float(arctap[7:-1])/500) + ' ' + str((float(x1)+progress(int(arctap[7:-1]))*(float(x2)-float(x1))-0.5)*scale) + ' 1 ' + ('1\n# 1.0\n& 1.0\n' if timingGroup[0] == 'noinput' else '0\n# 1.0\n& 1.0\n')
        elif 'scenecontrol' in line: pass
        elif 'camera' in line: pass
        else:
            t1,lane = line[1:-3].split(',')
            adjustScale(t1)
            judgeLine += 'n1 ' + str(cnt) + ' ' + str(float(t1)/500) + ' ' + x[int(lane)] + ' 1 ' + ('1\n# 1.0\n& 1.0\n' if timingGroup[0] == 'noinput' else '0\n# 1.0\n& 1.0\n')
    outChart += judgeLine
    cnt += 1
with open('chart.pec','w') as f: f.write(outChart)