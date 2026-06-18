#!/usr/bin/env python3
import csv, json, sys, os, urllib.request
from io import StringIO
from collections import Counter
from datetime import datetime

CSV_PATH = '/sessions/bold-peaceful-wright/mnt/uploads/Camellia.csv'
OUT_DIR = '/sessions/bold-peaceful-wright/mnt/outputs'

def parse_records(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    rows, cur, in_q = [], '', False
    for ch in content:
        if ch == '"': in_q = not in_q
        if ch == '\n' and not in_q:
            if cur.strip(): rows.append(cur)
            cur = ''
        else: cur += ch
    if cur.strip(): rows.append(cur)
    records = []
    for row in rows[1:]:
        fields = next(csv.reader(StringIO(row)))
        if len(fields) < 12: continue
        try:
            records.append({'t':int(fields[2]),'s':int(fields[4]),'ct':int(fields[5]),'c':fields[7],'tm':fields[8],'r':fields[9]})
        except: pass
    return records

def esc(s):
    if not s: return ''
    return s.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n').replace('\r','\\r')

def segment_words(text):
    known = ['你好','晚安','早安','早上','晚上','下午','中午','上午','今天','明天','昨天','后天',
        '睡觉','学习','吃饭','开心','难过','伤心','喜欢','讨厌','知道','觉得','感觉','可以',
        '没有','什么','怎么','为什么','因为','所以','但是','如果','虽然','而且','或者','还是',
        '已经','不要','可能','应该','需要','希望','谢谢','客气','加油','努力','工作','上课',
        '下课','放学','上学','考试','作业','论文','毕业','健身','运动','跑步','锻炼','瑜伽',
        '休息','加班','忙死','累死','笑死','哭死','想死','气死','烦死','困死','饿死',
        '哈哈','嘻嘻','嘿嘿','呵呵','呜呜','嗯嗯','哦哦','啊啊','好吧','好的','是的',
        '真的','假的','对的','算啦','完了','走了','来了','回来','出去','进来','起来',
        '一起','自己','我们','你们','他们','咱们','大家','朋友','同学','老师','老板',
        '天气','下雨','晴天','阴天','台风','下雪','刮风','打雷','闪电',
        '好吃','好看','好玩','好听','好喝','好冷','好热','好累','好困','好忙','好烦',
        '好棒','好帅','好美','好可爱','好喜欢','好开心','好难过','好伤心',
        '想我','想你','想他','想她','螺蛳粉','食堂','外卖','做饭','早餐','午餐','晚餐','晚饭','午饭',
        '洗澡','洗漱','护肤','化妆','打扮','穿搭','衣服','鞋子',
        '回家','出门','路上','堵车','打车','公交','地铁',
        '手机','电脑','充电','WiFi','信号','网络',
        '消息','电话','视频','语音','通话','聊天','发消息','打电话',
        '宝贝','宝宝','亲爱的','对不起','没关系','没事的','可以的','好吧','算了吧','随便吧',
        '不知道','不明白','不懂了','不会吧','不会的','不行啊','不好吧',
        '写论文','做实验','搞论文','改论文','查文献','去健身','去跑步','去运动','去上课','去学校','去食堂',
        '睡不着','不想睡','还没睡','快睡吧','早点睡','熬夜了','又熬夜',
        '哈哈哈','好家伙','不是吧','啊这','绝了','离谱','笑死了',
        '想你啦','想你呀','想你了','好想你','我也想','我也好想',
    ]
    res = {}
    for w in known:
        n = text.count(w)
        if n: res[w] = n
    return res

def build(recs):
    total=len(recs); tx=[r for r in recs if r['t']==1]; im=[r for r in recs if r['t']==3]; em=[r for r in recs if r['t']==47]; sy=[r for r in recs if r['t']==10000]
    st=Counter(r['r'] for r in recs); st_t=Counter(r['r'] for r in tx); st_i=Counter(r['r'] for r in im); st_e=Counter(r['r'] for r in em)
    sd=[]
    for i,(nm,c) in enumerate(st.most_common()):
        sd.append({'n':nm,'t':c,'tx':st_t.get(nm,0),'im':st_i.get(nm,0),'em':st_e.get(nm,0),'p':round(c/total*100,1),'c':['#6c5ce7','#fd79a8'][i%2]})
    da,da_t=Counter(),Counter()
    for r in recs: d=r['tm'][:10]; da[d]+=1
    if r['t']==1: da_t[d]+=1
    sd_=sorted(set(r['tm'][:10] for r in recs if r['tm']))
    dd=[{'d':d,'t':da.get(d,0),'x':da_t.get(d,0)} for d in sd_]
    hr=Counter()
    for r in recs:
        if r['tm']:
            try: hr[int(r['tm'][11:13])]+=1
            except: pass
    hd=[{'h':h,'t':hr.get(h,0)} for h in range(24)]
    wc=Counter(); wn=['周一','周二','周三','周四','周五','周六','周日']
    for r in recs:
        try: wc[datetime.strptime(r['tm'],'%Y-%m-%d %H:%M:%S').weekday()]+=1
        except: pass
    wd=[{'d':wn[d],'c':wc.get(d,0)} for d in range(7)]
    word_counter=Counter()
    for r in tx:
        for w,n in segment_words(r['c']).items(): word_counter[w]+=n
    tc=[{'c':w,'n':n} for w,n in word_counter.most_common(120)]
    tl=[len(r['c']) for r in tx if r['c']]
    al=round(sum(tl)/len(tl),1) if tl else 0; ml=max(tl) if tl else 0
    pv=None; rt=[]
    for r in recs:
        if pv and r['s']!=pv['s'] and pv['t']==1 and r['t']==1:
            d=r['ct']-pv['ct']
            if 0<d<86400: rt.append(d)
        pv=r
    ar=round(sum(rt)/len(rt)/60,1) if rt else 0
    sk=1; ms=1; cr=None
    for r in recs:
        if r['r']==cr and r['t'] in (1,3,47): sk+=1; ms=max(ms,sk)
        else: sk=1; cr=r['r']

    # Per-speaker reply stats with conversation period detection
    # A "conversation period" is: messages within 30 minutes of each other
    # If gap > 30 min, it's a new conversation period, and we don't count
    # the reply across periods as a "reply" (it's a new conversation)
    spk_rt={}; spk_ml={}; spk_rc={}; spk_fc={}; daily_f={}
    spk_fast={}; spk_med={}; spk_slow={}  # <30s, 30s-2min, >2min
    last_spk=None; last_t=None; last_s=None
    CONV_GAP = 1800  # 30 minutes = new conversation

    for r in recs:
        spk=r['r']
        if spk not in spk_rt: spk_rt[spk]=[]
        if spk not in spk_ml: spk_ml[spk]=[]
        if spk not in spk_rc: spk_rc[spk]=0
        if spk not in spk_fast: spk_fast[spk]=0
        if spk not in spk_med: spk_med[spk]=0
        if spk not in spk_slow: spk_slow[spk]=0
        if last_spk and last_spk!=spk and last_s!=r['s'] and r['t']==1:
            d=r['ct']-last_t
            # Only count as reply if within conversation period (30 min)
            if 0<d<CONV_GAP:
                spk_rt[spk].append(d)
                spk_rc[spk]+=1
                if d < 30: spk_fast[spk]+=1
                elif d < 120: spk_med[spk]+=1
                else: spk_slow[spk]+=1
        if r['t']==1: spk_ml[spk].append(len(r['c']))
        d_=r['tm'][:10]
        if d_ not in daily_f: daily_f[d_]=spk; spk_fc[spk]=spk_fc.get(spk,0)+1
        last_spk=spk; last_t=r['ct']; last_s=r['s']

    # Global stats - same logic
    global_rt=[]
    pv=None
    for r in recs:
        if pv and r['s']!=pv['s'] and pv['t']==1 and r['t']==1:
            d=r['ct']-pv['ct']
            if 0<d<CONV_GAP: global_rt.append(d)
        pv=r
    ar_seconds = round(sum(global_rt)/len(global_rt),1) if global_rt else 0
    ar_minutes = round(ar_seconds/60,1)
    global_fast = sum(1 for t in global_rt if t<30)
    global_med = sum(1 for t in global_rt if 30<=t<120)
    global_slow = sum(1 for t in global_rt if t>=120)

    COMP={}
    for s in st:
        rt_=spk_rt.get(s,[]); ml_=spk_ml.get(s,[]); fc=spk_fast.get(s,0); mc=spk_med.get(s,0); sc=spk_slow.get(s,0)
        total_r = fc+mc+sc
        COMP[s]={'as':round(sum(rt_)/len(rt_),1) if rt_ else 0,'fc':fc,'mc':mc,'sc':sc,'frp':round(fc/total_r*100,1) if total_r else 0,'mrp':round(mc/total_r*100,1) if total_r else 0,'srp':round(sc/total_r*100,1) if total_r else 0,'rc':total_r,'al':round(sum(ml_)/len(ml_),1) if ml_ else 0,'ml':max(ml_) if ml_ else 0,'fd':spk_fc.get(s,0)}

    pw=['好','棒','开心','喜欢','爱','美','漂亮','帅','厉害','优秀','幸福','快乐','晚安','早安','加油','不错','哈哈','嘻嘻','可爱','温柔','感动','期待','舒服','好看','好吃','好玩','赞']
    nw=['烦','累','困','难过','伤心','哭','气','生气','讨厌','恨','焦虑','压力','紧张','郁闷','崩溃','痛苦','倒霉','糟糕','差','失望','无聊','没意思','愁','唉','难受','委屈','心累']
    pwc=Counter(); nwc=Counter(); pwc_by={}; nwc_by={}; snt={}
    for r in tx:
        d_=r['tm'][:10]; spk=r['r']
        if d_ not in snt: snt[d_]=[0,0]
        if spk not in pwc_by: pwc_by[spk]=Counter()
        if spk not in nwc_by: nwc_by[spk]=Counter()
        for w in pw:
            n=r['c'].count(w)
            if n: pwc[w]+=n; pwc_by[spk][w]+=n; snt[d_][0]+=n
        for w in nw:
            n=r['c'].count(w)
            if n: nwc[w]+=n; nwc_by[spk][w]+=n; snt[d_][1]+=n
    snd=[{'d':d_,'p':snt[d_][0],'n':snt[d_][1]} for d_ in sorted(snt.keys())]
    wh=[[0]*24 for _ in range(7)]
    for r in recs:
        try: dt=datetime.strptime(r['tm'],'%Y-%m-%d %H:%M:%S'); wh[dt.weekday()][dt.hour]+=1
        except: pass
    mwh=max(max(row) for row in wh) if any(any(row) for row in wh) else 1
    spwr={}
    for s in st:
        spwr[s]={'p':[{'w':w,'c':pwc_by.get(s,{}).get(w,0)} for w in pw],'n':[{'w':w,'c':nwc_by.get(s,{}).get(w,0)} for w in nw]}
    return {'T':total,'TX':len(tx),'IM':len(im),'EM':len(em),'SY':len(sy),'AL':al,'ML':ml,'SD':sd,'SC':len(sd),'DD':dd,'HD':hd,'WD':wd,'WN':wn,'TC':tc,'SN':snd,'AR':ar_seconds,'MS':ms,'WH':wh,'MWH':mwh,'PW':[{'w':w,'c':pwc.get(w,0)} for w in pw],'NW':[{'w':w,'c':nwc.get(w,0)} for w in nw],'RNG':{'s':sd_[0],'e':sd_[-1],'d':len(sd_)},'SPWR':spwr,'COMP':COMP,'GR':{'as':ar_seconds,'fc':global_fast,'mc':global_med,'sc':global_slow,'tot':len(global_rt)}}

def gen_msgs(recs):
    li=['var CHAT_MESSAGES=[']
    for r in recs:
        c=r['c'] if r['t']==1 else ''
        if len(c)>300: c=c[:300]
        li.append("{t:%d,s:%d,c:'%s',tm:'%s',r:'%s'}," % (r['t'],r['s'],esc(c),esc(r['tm']),esc(r['r'])))
    li.append('];')
    return '\n'.join(li)

if __name__ == '__main__':
    print('[1] Download Chart.js...', file=sys.stderr)
    chartjs = ''
    for url in ['https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.0/chart.umd.min.js']:
        try:
            chartjs = urllib.request.urlopen(url, timeout=10).read().decode('utf-8')
            print('  OK (%dKB)' % (len(chartjs)//1024), file=sys.stderr)
            break
        except: pass
    if not chartjs: print('ERROR'); sys.exit(1)
    print('[2] Parse...', file=sys.stderr)
    recs = parse_records(CSV_PATH)
    print('  %d records' % len(recs), file=sys.stderr)
    S = build(recs)
    for s in S['SD']: print('  %s: %d (%d%%)' % (s['n'], s['t'], s['p']), file=sys.stderr)
    for s in S['COMP']: print('  %s reply: %s sec avg, fast:%d med:%d slow:%d avg_len:%d' % (s, S['COMP'][s]['as'], S['COMP'][s]['fc'], S['COMP'][s]['mc'], S['COMP'][s]['sc'], S['COMP'][s]['al']), file=sys.stderr)
    print('  Global: %s sec avg, fast:%d med:%d slow:%d' % (S['GR']['as'], S['GR']['fc'], S['GR']['mc'], S['GR']['sc']), file=sys.stderr)
    D=S

    # Prebuild UI parts
    sl = ''
    for s in D['SD']:
        pd = str(s['p'])+'%' if s['p']>8 else ''
        sl += '<div class="sb"><div class="nm">'+s['n']+'</div><div class="bw"><div class="bf" style="width:'+str(s['p'])+'%;background:'+s['c']+'">'+pd+'</div></div><div class="bv">'+str(s['t'])+'</div></div>'
        sl += '<div class="sdet"><span>\U0001f4dd '+str(s['tx'])+'</span><span>\U0001f5bc '+str(s['im'])+'</span><span>\U0001f60a '+str(s['em'])+'</span></div>'

    hm='<table style="border-collapse:collapse;font-size:11px;width:100%"><tr><td style="padding:4px;font-weight:600">时间</td>'
    for h in range(24): hm+='<td style="padding:2px;text-align:center;min-width:26px;font-size:9px">'+str(h)+'</td>'
    hm+='</tr>'
    for d in range(7):
        hm+='<tr><td style="padding:4px;font-weight:500">'+D['WN'][d]+'</td>'
        for h in range(24):
            v=D['WH'][d][h]; r=35+round(v/D['MWH']*180) if D['MWH'] else 35
            hm+='<td style="padding:2px;text-align:center;font-size:9px;color:'+('#fff' if r>130 else '#666')+';background:rgb('+str(255-r)+','+str(240-r)+',255)" title="'+D['WN'][d]+' '+str(h)+':00 - '+str(v)+'">'+(''if v==0 else str(v))+'</td>'
        hm+='</tr>'
    hm+='</table>'

    # Comparison table
    cp = D['COMP']; nms = list(cp.keys())
    comp_html = ''
    if len(nms) >= 2:
        a,b = nms[0],nms[1]
        ca,cb = D['SD'][0]['c'],D['SD'][1]['c']
        mx_as = max(1, cp[a]['as'], cp[b]['as'])
        mx_al = max(1, cp[a]['al'], cp[b]['al'])
        mx_fd = max(1, cp[a]['fd'], cp[b]['fd'])
        mx_rc = max(1, cp[a]['rc'], cp[b]['rc'])
        # 3 speed tiers: fast(<30s), med(30s-2min), slow(>2min) - show as stacked
        comp_html = '<div class="cd fw"><h2>\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466 两人对比 <span class="bd">回复速度 · 字数 · 主动性</span></h2>'
        comp_html += '<table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:8px">'
        comp_html += '<tr style="border-bottom:2px solid #dfe6e9"><td style="padding:10px 8px;font-weight:600">指标</td>'
        for s in D['SD']: comp_html += '<td style="padding:10px 8px;font-weight:600;color:'+s['c']+'">'+s['n']+'</td>'
        comp_html += '</tr>'
        rows = [
            ('\U0001f4ec 平均回复', str(cp[a]['as'])+'秒', str(cp[b]['as'])+'秒', None, None, None),
            ('⚡ 快速(<30s)', str(cp[a]['fc'])+'次('+str(cp[a]['frp'])+'%)', str(cp[b]['fc'])+'次('+str(cp[b]['frp'])+'%)', None, None, None),
            ('\U0001f3c3 中速(30s-2min)', str(cp[a]['mc'])+'次('+str(cp[a]['mrp'])+'%)', str(cp[b]['mc'])+'次('+str(cp[b]['mrp'])+'%)', None, None, None),
            ('\U0001f438 慢速(>2min)', str(cp[a]['sc'])+'次('+str(cp[a]['srp'])+'%)', str(cp[b]['sc'])+'次('+str(cp[b]['srp'])+'%)', None, None, None),
            ('\U0001f4dd 平均字数', str(cp[a]['al'])+'字', str(cp[b]['al'])+'字', None, None, None),
            ('\U0001f4e4 回复次数', str(cp[a]['rc'])+'次', str(cp[b]['rc'])+'次', None, mx_rc, mx_rc),
            ('\U0001f305 率先说话', str(cp[a]['fd'])+'天', str(cp[b]['fd'])+'天', None, mx_fd, mx_fd),
        ]
        for lb, va, vb, _, mx1, mx2 in rows:
            comp_html += '<tr style="border-bottom:1px solid #f0f0f0"><td style="padding:8px;font-weight:500">'+lb+'</td>'
            comp_html += '<td style="padding:8px;font-weight:600;color:'+ca+'">'+va+'</td>'
            comp_html += '<td style="padding:8px;font-weight:600;color:'+cb+'">'+vb+'</td></tr>'
        comp_html += '</table>'
        # Add speed distribution bars (stacked)
        mx_sp = max(1, cp[a]['rc'], cp[b]['rc'])
        def speed_bar(spk, mx):
            fc=cp[spk]['fc']; mc=cp[spk]['mc']; sc=cp[spk]['sc']
            fw=fc/mx*100; mw=mc/mx*100; sw=sc/mx*100
            return '<div style="height:24px;display:flex;border-radius:12px;overflow:hidden;margin:4px 0">'+\
                ('<div style="width:'+str(fw)+'%;background:#00b894;display:flex;align-items:center;justify-content:center;font-size:9px;color:#fff">'+(''if fw<6 else str(fc))+'</div>' if fc else '')+\
                ('<div style="width:'+str(mw)+'%;background:#fdcb6e;display:flex;align-items:center;justify-content:center;font-size:9px;color:#fff">'+(''if mw<6 else str(mc))+'</div>' if mc else '')+\
                ('<div style="width:'+str(sw)+'%;background:#e17055;display:flex;align-items:center;justify-content:center;font-size:9px;color:#fff">'+(''if sw<6 else str(sc))+'</div>' if sc else '')+'</div>'
        comp_html += '<div class="r2" style="margin-top:12px"><div class="cd"><h2 style="font-size:13px">\U0001f534 回复速度分布</h2>'
        comp_html += '<div style="display:flex;gap:4px;font-size:11px;margin-bottom:4px"><span style="color:#00b894">■ 快速</span><span style="color:#fdcb6e">■ 中速</span><span style="color:#e17055">■ 慢速</span></div>'
        for s in D['SD']: comp_html += '<div style="margin:8px 0"><span style="font-size:12px;font-weight:500;color:'+s['c']+'">'+s['n']+'</span>'+speed_bar(s['n'], mx_sp)+'</div>'
        comp_html += '</div><div class="cd"><h2 style="font-size:13px">\U0001f4ca 全局回复</h2>'
        comp_html += '<div class="rst"><div class="bg">'+str(D['GR']['as'])+'</div><div class="sm">平均回复(秒)</div></div>'
        comp_html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-top:8px">'
        comp_html += '<div class="rst" style="padding:8px"><div class="bg" style="font-size:20px">'+str(D['GR']['fc'])+'</div><div class="sm" style="font-size:11px">快速\n&lt;30s</div></div>'
        comp_html += '<div class="rst" style="padding:8px"><div class="bg" style="font-size:20px">'+str(D['GR']['mc'])+'</div><div class="sm" style="font-size:11px">中速\n30s~2min</div></div>'
        comp_html += '<div class="rst" style="padding:8px"><div class="bg" style="font-size:20px">'+str(D['GR']['sc'])+'</div><div class="sm" style="font-size:11px">慢速\n&gt;2min</div></div>'
        comp_html += '</div></div></div></div>\n'
    else:
        comp_html = '<div class="r2"><div class="cd"><h2>\U0001f4ec 回复速度</h2><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">'
        comp_html += '<div class="rst"><div class="bg">'+str(D['GR']['as'])+'</div><div class="sm">平均(秒)</div></div>'
        comp_html += '<div class="rst"><div class="bg">'+str(D['GR']['fc'])+'</div><div class="sm">快速</div></div>'
        comp_html += '<div class="rst"><div class="bg">'+str(D['GR']['sc'])+'</div><div class="sm">慢速</div></div></div></div>'

    hdr = '%s ~ %s · %d天 · %d条 · %d人' % (D['RNG']['s'], D['RNG']['e'], D['RNG']['d'], D['T'], D['SC'])
    peak_h = max(h['t'] for h in D['HD'])
    pos_sum = sum(d['p'] for d in D['SN']); neg_sum = sum(d['n'] for d in D['SN'])

    # Sentiment tabs
    tabs=''; tcnt=''; first=True
    for s in D['SD']:
        nm=s['n']; ac=' active' if first else ''; ac2=' active' if first else ''
        tabs+='<button class="tab small'+ac+'" onclick="switchSent(\''+nm+'\')">'+nm+'</button>'
        # Build per-speaker word bars
        pw_=D['SPWR'][nm]['p']; nw_=D['SPWR'][nm]['n']
        mx_p=max(w['c'] for w in pw_) if max(w['c'] for w in pw_) else 1
        mx_n=max(w['c'] for w in nw_) if max(w['c'] for w in nw_) else 1
        pb=''; nb=''
        for w in pw_[:10]:
            wd = min(w['c']/mx_p*100,100) if mx_p else 0
            pb+='<div class="sb"><div class="nm">'+w['w']+'</div><div class="bw"><div class="bf" style="width:'+str(wd)+'%;background:#00b894">'+(''if w['c']==0 else str(w['c']))+'</div></div><div class="bv">'+str(w['c'])+'次</div></div>'
        for w in nw_[:10]:
            wd = min(w['c']/mx_n*100,100) if mx_n else 0
            nb+='<div class="sb"><div class="nm">'+w['w']+'</div><div class="bw"><div class="bf" style="width:'+str(wd)+'%;background:#e17055">'+(''if w['c']==0 else str(w['c']))+'</div></div><div class="bv">'+str(w['c'])+'次</div></div>'
        tcnt+='<div class="sent-tab'+ac2+'" id="sent-'+nm+'"><div class="r2" style="margin-top:8px"><div class="cd"><h2>\U0001f604 积极词</h2>'+pb+'</div><div class="cd"><h2>\U0001f622 消极词</h2>'+nb+'</div></div></div>'
        first=False

    jdata = json.dumps(S, ensure_ascii=False)
    html = '﻿<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Camellia 聊天分析</title>\n<script>'+chartjs+'</script>\n<style>\n'
    css = '''*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:#f0f2f5;color:#2d3436}
.hdr{background:linear-gradient(135deg,#6c5ce7,#a29bfe);color:#fff;padding:24px 32px}
.hdr h1{font-size:26px;font-weight:700}.hdr p{font-size:14px;opacity:.85;margin-top:4px}
.ct{max-width:1400px;margin:0 auto;padding:20px}
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}
.sc{background:#fff;border-radius:12px;padding:18px;box-shadow:0 2px 10px rgba(0,0,0,.08)}
.sc .lb{font-size:12px;color:#636e72;margin-bottom:4px}.sc .vl{font-size:26px;font-weight:700}.sc .sb{font-size:11px;color:#636e72;margin-top:2px}.sc .ic{float:right;font-size:24px;opacity:.25}
.r2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
@media(max-width:900px){.r2{grid-template-columns:1fr}}
.cd{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,.08)}
.cd h2{font-size:15px;font-weight:600;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #dfe6e9;display:flex;align-items:center;gap:8px}
.cd h2 .bd{font-size:10px;font-weight:400;background:#a29bfe;color:#fff;border-radius:10px;padding:2px 8px;margin-left:auto}
.ch{position:relative;height:260px}.fw{grid-column:1/-1}.srch{margin-bottom:24px}
.sb2{display:flex;gap:10px;margin-bottom:12px}
.sb2 input{flex:1;padding:12px 16px;border:2px solid #dfe6e9;border-radius:10px;font-size:15px;outline:0}
.sb2 input:focus{border-color:#6c5ce7}
.sb2 button{padding:12px 24px;background:#6c5ce7;color:#fff;border:none;border-radius:10px;font-size:15px;cursor:pointer;font-weight:600}
.sh{font-size:13px;color:#636e72;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:4px}
.sh sp{display:inline-block;background:#dfe6e9;border-radius:4px;padding:2px 10px;font-size:12px;cursor:pointer}
.sh sp:hover{background:#a29bfe;color:#fff}
.sres{max-height:400px;overflow-y:auto;background:#fff;border-radius:8px}
.sri{padding:10px 14px;border-bottom:1px solid #dfe6e9;font-size:14px;line-height:1.6}
.sri:last-child{border-bottom:none}.sri .mt{font-size:11px;color:#636e72;margin-bottom:2px}.sri .hl{background:#ffeaa7;border-radius:2px;padding:0 2px}
.sb{display:flex;align-items:center;gap:12px;padding:6px 0}
.sb .nm{min-width:70px;font-weight:500;font-size:13px}
.sb .bw{flex:1;height:22px;background:#f0f0f0;border-radius:11px;overflow:hidden}
.sb .bf{height:100%;border-radius:11px;display:flex;align-items:center;padding-left:6px;font-size:10px;color:#fff;white-space:nowrap}
.sb .bv{font-size:12px;color:#636e72;min-width:36px;text-align:right}
.sdet{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;font-size:11px;color:#636e72;padding-bottom:8px}
.wc{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 12px;padding:10px;min-height:200px}
.wc sp{transition:transform .2s;cursor:default;display:inline-block;white-space:nowrap}
.wc sp:hover{transform:scale(1.3);color:#6c5ce7!important}
.tabs{display:flex;gap:2px;background:#dfe6e9;padding:3px;border-radius:10px;margin-bottom:16px}
.tab{flex:1;padding:8px 12px;border:none;background:transparent;border-radius:8px;font-size:13px;cursor:pointer;font-weight:500;text-align:center}
.tab.active{background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.1);color:#6c5ce7}
.tab.small{flex:0 1 auto;padding:6px 16px;font-size:12px}
.tc{display:none}.tc.active{display:block}
.sent-tab{display:none}.sent-tab.active{display:block}
.rst{text-align:center;padding:12px}.rst .bg{font-size:30px;font-weight:700;color:#6c5ce7}.rst .sm{font-size:12px;color:#636e72;margin-top:2px}
.hg{display:flex;flex-wrap:wrap;gap:2px;max-height:120px;overflow-y:auto}.hg div{cursor:pointer;border-radius:2px}
''' + '</style>\n</head>\n<body>\n'
    html += css
    html += '<div class="hdr"><h1>\U0001f4ac 聊天记录分析仪表盘</h1><p>'+hdr+'</p></div>\n<div class="ct" id="app">\n'

    # Stats grid
    html += '<div class="sg">\n'
    items = [('\U0001f4ac','总消息',str(D['T']),str(D['RNG']['d'])+' 天'),
        ('\U0001f4dd','文本',str(D['TX']),'{:.1f}%'.format(D['TX']/D['T']*100)),
        ('\U0001f5bc','图片',str(D['IM']),'{:.1f}%'.format(D['IM']/D['T']*100)),
        ('\U0001f60a','表情',str(D['EM']),'{:.1f}%'.format(D['EM']/D['T']*100)),
        ('\U0001f4cf','平均字数',str(D['AL']),'最长 '+str(D['ML'])),
        ('\U0001f465','人数',str(D['SC']),'、'.join(s['n'] for s in D['SD']))]
    for icon,lb,vl,sb in items:
        html += '<div class="sc"><div class="ic">'+icon+'</div><div class="lb">'+lb+'</div><div class="vl">'+vl+'</div><div class="sb">'+sb+'</div></div>\n'
    html += '</div>\n'

    # Search
    html += '<div class="cd srch"><h2>\U0001f50d 语义搜索 <span class="bd">近义词扩展</span></h2>\n'
    html += '<div class="sb2"><input id="si" placeholder="输入关键词，自动匹配近义词" onkeydown="if(event.key===\'Enter\')doSearch()"><button onclick="doSearch()">\U0001f50d 搜索</button></div>\n'
    html += '<div class="sh"><sp onclick="tagSearch(this)">睡觉</sp><sp onclick="tagSearch(this)">学习</sp><sp onclick="tagSearch(this)">吃饭</sp><sp onclick="tagSearch(this)">开心</sp><sp onclick="tagSearch(this)">难过</sp><sp onclick="tagSearch(this)">天气</sp><sp onclick="tagSearch(this)">健身</sp><sp onclick="tagSearch(this)">你好</sp><sp onclick="tagSearch(this)">想</sp></div>\n'
    html += '<div id="sr" class="sres"></div></div>\n'

    # Tabs
    html += '<div class="tabs"><button class="tab active" data-t="overview">\U0001f4ca 概览</button><button class="tab" data-t="activity">\U0001f4c8 活跃</button><button class="tab" data-t="sentiment">\U0001f60a 情感</button><button class="tab" data-t="words">\U0001f524 词云</button></div>\n'

    # Overview tab
    html += '<div class="tc active" id="t-overview"><div class="r2">\n'
    html += '<div class="cd"><h2>\U0001f464 发言者</h2><div class="ch"><canvas id="spc"></canvas></div><div id="sl">'+sl+'</div></div>\n'
    html += '<div class="cd"><h2>\U0001f4ca 消息类型</h2><div class="ch"><canvas id="tc"></canvas></div></div></div>\n'
    html += comp_html
    html += '<div class="cd fw"><h2>\U0001f5d3 每日趋势 <span class="bd">'+str(D['RNG']['d'])+'天</span></h2><div class="ch"><canvas id="dc"></canvas></div></div></div>\n'

    # Activity tab
    html += '<div class="tc" id="t-activity"><div class="r2">'
    html += '<div class="cd"><h2>⏰ 小时分布 <span class="bd">峰值'+str(peak_h)+'条</span></h2><div class="ch"><canvas id="hc"></canvas></div></div>'
    html += '<div class="cd"><h2>\U0001f4c5 星期分布</h2><div class="ch"><canvas id="wc"></canvas></div></div></div>'
    html += '<div class="cd fw"><h2>\U0001f525 星期×小时热力</h2><div style="overflow-x:auto">'+hm+'</div></div>'
    html += '<div class="cd fw" style="margin-top:16px"><h2>\U0001f4ca 每日热度 <span class="bd">'+str(len(D['DD']))+'天</span></h2><div class="hg" id="hm"></div></div></div>'

    # Sentiment tab
    html += '<div class="tc" id="t-sentiment">'
    html += '<div class="cd fw"><h2>\U0001f60a 情感趋势 <span class="bd">积极'+str(pos_sum)+' · 消极'+str(neg_sum)+'</span></h2><div class="ch"><canvas id="sc"></canvas></div></div>'
    html += '<div class="tabs" style="margin-top:12px">'+tabs+'</div>'+tcnt+'</div>'

    # Word cloud tab
    html += '<div class="tc" id="t-words"><div class="cd"><h2>\U0001f524 常用词汇 <span class="bd">词组 · 字号越大越频繁</span></h2><div class="wc" id="wcloud"></div></div></div></div>'

    # JS
    html += '<script>\nvar D=' + jdata + ';\nvar _messages=null;var _msgLoaded=false;\n'
    html += "var syms={\n"+"".join("  '%s':%s,\n" % (k,v) for k,v in [
        ("你好","['你好','嗨','hi','hello','hey','你好呀','早','晚安','晚上好','下午好']"),
        ("晚安","['晚安','安','睡了','睡觉','好梦','night']"),
        ("吃饭","['吃','饭','食堂','早餐','午餐','晚餐','晚饭','午饭','美食','好吃','螺蛳粉']"),
        ("学习","['学习','论文','写论文','上课','考试','作业','复习','研究','实验','读书','毕业','课']"),
        ("健身","['健身','锻炼','运动','跑步','瑜伽','撸铁']"),
        ("睡觉","['睡','睡觉','休息','困','熬夜','早起','晚安','好梦','睡眠','失眠']"),
        ("开心","['开心','高兴','快乐','哈哈','嘻嘻','嘿嘿','棒','幸福','笑']"),
        ("难过","['难过','伤心','哭','不开心','委屈','难受','心累','郁闷','崩溃']"),
        ("天气","['天气','下雨','晴天','阴天','台风','雨','冷','热','暖']"),
        ("忙碌","['忙','好忙','忙死','累','好累','忙完','一直忙','最近忙']"),
        ("想","['想','想你','思念','念','惦记','牵','想我']"),
        ("早安","['早安','早','早上好','早晨','早呀','早哦']"),
    ])+"};\n"
    html += '''
window.addEventListener('load',function(){drawCharts();drawWC();drawHM();});
function drawCharts(){
  new Chart(document.getElementById('spc').getContext('2d'),{type:'doughnut',data:{labels:D.SD.map(function(s){return s.n}),datasets:[{data:D.SD.map(function(s){return s.t}),backgroundColor:D.SD.map(function(s){return s.c}),borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}}}});
  new Chart(document.getElementById('tc').getContext('2d'),{type:'bar',data:{labels:['文本','图片','表情','系统','其他'],datasets:[{label:'数量',data:[D.TX,D.IM,D.EM,D.SY,D.T-D.TX-D.IM-D.EM-D.SY],backgroundColor:['#6c5ce7','#00b894','#fd79a8','#dfe6e9','#fdcb6e'],borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'#f0f0f0'}},x:{grid:{display:false}}}}});
  new Chart(document.getElementById('dc').getContext('2d'),{type:'line',data:{labels:D.DD.map(function(d){return d.d.slice(5)}),datasets:[{label:'全部',data:D.DD.map(function(d){return d.t}),borderColor:'#6c5ce7',backgroundColor:'rgba(108,92,231,0.06)',fill:true,tension:0.3,pointRadius:2},{label:'文本',data:D.DD.map(function(d){return d.x}),borderColor:'#fd79a8',backgroundColor:'rgba(253,121,168,0.06)',fill:true,tension:0.3,pointRadius:2}]},options:{responsive:true,maintainAspectRatio:false,interaction:{intersect:false,mode:'index'},plugins:{legend:{position:'top',labels:{boxWidth:12}}},scales:{x:{grid:{display:false},ticks:{maxTicksLimit:20}},y:{beginAtZero:true,grid:{color:'#f0f0f0'}}}}});
  var mh=Math.max.apply(null,D.HD.map(function(d){return d.t}));
  new Chart(document.getElementById('hc').getContext('2d'),{type:'bar',data:{labels:D.HD.map(function(d){return d.h+'时'}),datasets:[{label:'消息',data:D.HD.map(function(d){return d.t}),backgroundColor:D.HD.map(function(d){return d.t>mh*0.7?'#e17055':d.t>mh*0.4?'#fdcb6e':'#a29bfe'}),borderRadius:4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'#f0f0f0'}},x:{grid:{display:false}}}}});
  new Chart(document.getElementById('wc').getContext('2d'),{type:'bar',data:{labels:D.WD.map(function(d){return d.d}),datasets:[{label:'消息',data:D.WD.map(function(d){return d.c}),backgroundColor:'#6c5ce7',borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'#f0f0f0'}},x:{grid:{display:false}}}}});
  new Chart(document.getElementById('sc').getContext('2d'),{type:'line',data:{labels:D.SN.map(function(d){return d.d.slice(5)}),datasets:[{label:'积极',data:D.SN.map(function(d){return d.p}),borderColor:'#00b894',backgroundColor:'rgba(0,184,148,0.08)',fill:true,tension:0.3,pointRadius:2},{label:'消极',data:D.SN.map(function(d){return d.n}),borderColor:'#e17055',backgroundColor:'rgba(225,112,85,0.08)',fill:true,tension:0.3,pointRadius:2}]},options:{responsive:true,maintainAspectRatio:false,interaction:{intersect:false,mode:'index'},plugins:{legend:{position:'top',labels:{boxWidth:12}}},scales:{x:{grid:{display:false},ticks:{maxTicksLimit:15}},y:{beginAtZero:true,grid:{color:'#f0f0f0'}}}}});
}
function drawWC(){
  if(!D.TC||!D.TC.length)return;var mc=D.TC[0].n,h='';
  D.TC.forEach(function(c){var s=14+(c.n/mc)*36,h2=260-(c.n/mc)*60;h+='<sp style="font-size:'+s+'px;color:hsl('+h2+',60%,50%)">'+c.c+'</sp>';});
  document.getElementById('wcloud').innerHTML=h;
}
function drawHM(){
  if(!D.DD||!D.DD.length)return;var max=0;D.DD.forEach(function(d){if(d.t>max)max=d.t});
  var h='';D.DD.forEach(function(d){var r=d.t/max,g=Math.round(225-r*80);h+='<div title="'+d.d+': '+d.t+'条" style="width:14px;height:14px;background:rgb('+Math.round(230-r*80)+','+g+',255);display:flex;align-items:center;justify-content:center;color:'+(r>0.5?'#fff':'#666')+'">&middot;</div>';});
  document.getElementById('hm').innerHTML=h;
}
document.querySelectorAll('.tab').forEach(function(b){b.addEventListener('click',function(){var t=this.dataset.t;if(t){document.querySelectorAll('.tab[data-t]').forEach(function(x){x.classList.remove('active')});document.querySelectorAll('.tc').forEach(function(x){x.classList.remove('active')});this.classList.add('active');document.getElementById('t-'+t).classList.add('active');}});});
function switchSent(nm){document.querySelectorAll('#t-sentiment .tab.small').forEach(function(x){x.classList.remove('active')});document.querySelectorAll('.sent-tab').forEach(function(x){x.classList.remove('active')});document.getElementById('sent-'+nm).classList.add('active');var btns=document.querySelectorAll('#t-sentiment .tab.small');for(var i=0;i<btns.length;i++){if(btns[i].textContent===nm)btns[i].classList.add('active');}}
function loadMsgs(cb){if(_msgLoaded){if(cb)cb();return;}document.getElementById('sr').innerHTML='<div style="padding:20px;text-align:center;color:#636e72">⏳ 加载消息数据...</div>';var s=document.createElement('script');s.src='chat_messages.js?'+Date.now();s.onload=function(){_msgLoaded=true;_messages=typeof CHAT_MESSAGES!=='undefined'?CHAT_MESSAGES:[];if(cb)cb();};s.onerror=function(){document.getElementById('sr').innerHTML='<div style="padding:20px;text-align:center;color:#e17055">⚠️ 加载失败，确认 chat_messages.js 在同目录</div>';};document.body.appendChild(s);setTimeout(function(){if(typeof CHAT_MESSAGES!=='undefined'){_messages=CHAT_MESSAGES;_msgLoaded=true;if(cb)cb();}},300);}
function tagSearch(el){document.getElementById('si').value=el.textContent;doSearch();}
function doSearch(){
  var q=document.getElementById('si').value.trim();
  if(!q){document.getElementById('sr').innerHTML='';return;}
  var el=document.getElementById('sr');
  el.innerHTML='<div style="padding:20px;text-align:center;color:#636e72">⏳ 搜索中...</div>';
  loadMsgs(function(){
    if(!_messages||!_messages.length){el.innerHTML='<p style="padding:20px;text-align:center;color:#e17055">消息数据为空</p>';return;}
    var kw=[q];
    for(var k in syms){if(syms[k].some(function(v){return v.indexOf(q)>=0||q.indexOf(v)>=0||k.indexOf(q)>=0||q.indexOf(k)>=0;}))kw=kw.concat(syms[k]);}
    kw=Array.from(new Set(kw));
    var res=[];for(var i=0;i<_messages.length;i++){var m=_messages[i];if(m.t!==1)continue;for(var j=0;j<kw.length;j++){if(m.c.indexOf(kw[j])>=0){res.push({m:m,w:kw[j]});break;}}if(res.length>=200)break;}
    var rl=kw.filter(function(k){return k!==q});
    var h='<div style="padding:12px;background:#f8f9fa;border-radius:8px;margin-bottom:12px"><strong>🔍 搜索: </strong>'+q+' <span style="font-size:13px;color:#636e72">'+res.length+'条结果</span>'+(rl.length?' <span style="font-size:12px;color:#636e72">近义词: '+rl.join('、')+'</span>':'')+'</div>';
    if(!res.length){h+='<p style="padding:20px;text-align:center;color:#636e72">无结果</p>';el.innerHTML=h;return;}
    for(var k=0;k<res.length;k++){var r=res[k],txt=r.m.c||'',idx=txt.indexOf(r.w),dsp=txt;if(idx>=0){var st=Math.max(0,idx-15);dsp=(st>0?'…':'')+txt.substring(st,idx)+'<span class="hl">'+txt.substring(idx,idx+r.w.length)+'</span>'+txt.substring(idx+r.w.length,idx+90);}h+='<div class="sri"><div class="mt">'+r.m.r+' '+(r.m.s===1?'(我)':'')+' | '+r.m.tm+'</div><div>'+dsp+'</div></div>';}
    el.innerHTML=h;
  });
}
</script>
</body>
</html>'''

    path = os.path.join(OUT_DIR, 'chat_analysis.html')
    with open(path, 'w', encoding='utf-8') as f: f.write(html)
    print('-> %s (%dKB)' % (path, len(html)//1024), file=sys.stderr)

    print('[3] Messages...', file=sys.stderr)
    msgs = gen_msgs(recs)
    mpath = os.path.join(OUT_DIR, 'chat_messages.js')
    with open(mpath, 'w', encoding='utf-8') as f: f.write(msgs)
    print('-> %s (%.1fMB)' % (mpath, len(msgs)/1024/1024), file=sys.stderr)
    print('Done!', file=sys.stderr)
                                                    