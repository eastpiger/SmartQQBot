# coding: utf-8
import json
import urllib
import logging
import time
import datetime
import os
import random
from random import randint
import re
from smart_qq_bot.signals import on_group_message, on_private_message

pretime = [datetime.datetime(2000,1,1), datetime.datetime(2000,1,1)]
delta = datetime.timedelta(hours=1)

##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_p=re.compile('</p>')#处理换行
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_p.sub('\n',s)#将br转换为换行
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    # blank_line=re.compile('\n+')
    # s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如>
        key=sz.group('name')#去除&;后entity,如>为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def maimeng():
    maimeng_list = [
        '(●´∀｀●)',
        '⁽⁽٩( ´͈ ᗨ `͈ )۶⁾⁾',
        'ヽ(≧∀≦)ﾉ',
        '(´｡✪ω✪｡｀)',
        '(⑉• •⑉)‥♡',
        '٩(๑^o^๑)۶',
        '(=^ェ^=)',
        '✧٩(ˊωˋ*)و✧',
        '(๑•́ ₃ •̀๑)',
        '(๑＞ڡ＜)☆ ',
        '(≧▽≦)',
        '(๑´•.̫ • `๑)',
        'ﾍ(ﾟ∀ﾟﾍ)',
    ]
    temp = random.randrange(0,12,1)
    return maimeng_list[temp]

def try_faq(content, bot):
    response = bot.client.get('http://v3.faqrobot.org/servlet/AQ?s=p&sysNum=146129551966011507&sourceId=0&timestamp={0}&dataType=json'
        .format(
            bot.client.get_timestamp(),
            ))

    response = json.loads(bot.client.get('http://v3.faqrobot.org/servlet/AQ?s=aq&timestamp={0}&dataType=json&{1}'
        .format(
            bot.client.get_timestamp(),
            urllib.parse.urlencode({
                'question': content
                })
            )))
    if response['robotAnswer'][0]['question']:
        return response['robotAnswer'][0]['ansCon']
    else:
        temp = random.randrange(0,300,1)
        if temp <= 1:
            return '大家好，我是上科大GeekPie机器人，我的后台服务器会根据历史咨询问题主动回答大家的问题。为了不过分打扰大家的咨询，我在招生群内的能力都是被压制的，加我为好友私聊时，我提供更多信息问答服务。'
        return None

def try_faq_p(content, bot):
    response = bot.client.get('http://v3.faqrobot.org/servlet/AQ?s=p&sysNum=146129551966011507&sourceId=0&timestamp={0}&dataType=json'
        .format(
            bot.client.get_timestamp(),
            ))

    response = json.loads(bot.client.get('http://v3.faqrobot.org/servlet/AQ?s=aq&timestamp={0}&dataType=json&{1}'
        .format(
            bot.client.get_timestamp(),
            urllib.parse.urlencode({
                'question': content
                })
            )))
    if response['robotAnswer'][0]['question']:
        return response['robotAnswer'][0]['ansCon']
    elif response['robotAnswer'][0]['gusList']:
        t = ''
        for i in response['robotAnswer'][0]['gusList']:
            t += '\n    【{}】'.format(i['question'])
        return '您要问的是不是：' + t
    else:
        return None

@on_group_message(name="faq")
def send_msg(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
#     if bot.gid_to_name(msg.from_uin) == '好好学习天天向上':
#         nowtime = datetime.datetime.now()
#         timedelta = nowtime - pretime[0]
#         if timedelta >= delta:
#             pretime[0] = nowtime
#             t += '''1.  上海考生须知：
# 各位上海同学、家长：如果对综评有纠结的可以打电话到4009209393或者18930933479，报上考生的情况，了解是否有录取的可能。请报出完整信息，包括姓名、高考裸分和加分。这三个都要报的。我们会针对个人给出相应信息。分数线现在肯定出不来，因为还没到最后投档的时候，请各位知悉。电话的人会比较多，如果占线请稍候再试试，也请打电话简明扼要，不要影响其他人打进来，谢谢！

# 2.  外省市考生须知：
# （1） 请问在X X省的招生计划数是多少？
# 请查看您所在省份的招生计划书（俗称“大厚本”），在提前批次可以找到我校的招生计划数。各地招生计划数、历年分数线、具体录取流程请咨询当地本科招生小组，或参考各高中统订统发的由地方考试院出版的《招生目录》或《志愿填报手册》等出版物。

# （2）高考出分后请及时反馈高考成绩（江苏省不需要反馈）：http://admission.shanghaitech.edu.cn/score_2016.php

# （3）如有问题请及时与我校在的当地本科招生小组取得联系，联系方式表http://asa.shanghaitech.edu.cn/admission_detail.asp?id=136
# 各地招生计划数、历年分数线、具体录取流程及其他报考问题，均可直接拨打当地招生小组的电话咨询，仅在招生群内咨询没有办法回答。另外，请注意在开通时间内咨询。

# 重要提示：除江苏省有特殊政策，需要获得开放日加分方可报考外，全国其他地区考生可在提前批次第一志愿填报我校。上科大录取按高考分+校园开放日加分后的总分降序排序，择优录取。

# [我是机器人，不要调戏我，谢谢~{}]
# '''.format(maimeng())
#             bot.reply_msg(msg, t)
        # t = try_faq(msg.content, bot)
        # if t:
        #     t = filter_tags(t)
        #     t += '\n----\n{}我是上科大GeekPie机器人。加好友私聊提供更多信息问答服务。'.format(maimeng())
        #     while len(t) > 400:
        #         bot.reply_msg(msg, t[:400])
        #         t = t[400:]
        #         time.sleep(3)
        #     bot.reply_msg(msg, t)
    # if bot.gid_to_name(msg.from_uin) in ('上科大本招咨询①群', '上科大本招咨询②群'):
    #     t = try_faq(msg.content, bot)
    #     if t:
    #         t = filter_tags(t)
    #         t += '\n----\n{}我是上科大GeekPie机器人。加好友私聊提供更多信息问答服务。'.format(maimeng())
    #         while len(t) > 400:
    #             bot.reply_msg(msg, t[:400])
    #             t = t[400:]
    #             time.sleep(3)
    #         bot.reply_msg(msg, t)

    if bot.gid_to_name(msg.from_uin) == '上科大本招咨询①群':
        nowtime = datetime.datetime.now()
        timedelta = nowtime - pretime[0]
        if timedelta >= delta:
            pretime[0] = nowtime
            t = ['''1.  上海考生须知：
各位上海同学、家长：如果对综评有纠结的可以打电话到4009209393或者18930933479，报上考生的情况，了解是否有录取的可能。请报出完整信息，包括姓名、高考裸分和加分。这三个都要报的。我们会针对个人给出相应信息。分数线现在肯定出不来，因为还没到最后投档的时候，请各位知悉。电话的人会比较多，如果占线请稍候再试试，也请打电话简明扼要，不要影响其他人打进来，谢谢！''',
'''2.  外省市考生须知：
（1） 请问在X X省的招生计划数是多少？
请查看您所在省份的招生计划书（俗称“大厚本”），在提前批次可以找到我校的招生计划数。各地招生计划数、历年分数线、具体录取流程请咨询当地本科招生小组，或参考各高中统订统发的由地方考试院出版的《招生目录》或《志愿填报手册》等出版物。

（2）高考出分后请及时反馈高考成绩（江苏省不需要反馈）：http://admission.shanghaitech.edu.cn/score_2016.php''',

'''（3）如有问题请及时与我校在的当地本科招生小组取得联系，联系方式表http://asa.shanghaitech.edu.cn/admission_detail.asp?id=136
各地招生计划数、历年分数线、具体录取流程及其他报考问题，均可直接拨打当地招生小组的电话咨询，仅在招生群内咨询没有办法回答。另外，请注意在开通时间内咨询。''',

'''重要提示：除江苏省有特殊政策，需要获得开放日加分方可报考外，全国其他地区考生可在提前批次第一志愿填报我校。上科大录取按高考分+校园开放日加分后的总分降序排序，择优录取。''']
            for i in range(len(t)):
                bot.reply_msg(msg, t[i] + '\n[{}/{} 我是机器人，被主人逼迫来这里发公告，请不要调戏我，谢谢~{}]'.format(i + 1, len(t), maimeng()))
                time.sleep(3)

    if bot.gid_to_name(msg.from_uin) == '上科大本招咨询②群':
        nowtime = datetime.datetime.now()
        timedelta = nowtime - pretime[1]
        if timedelta >= delta:
            pretime[1] = nowtime
            t = ['''1.  上海考生须知：
各位上海同学、家长：如果对综评有纠结的可以打电话到4009209393或者18930933479，报上考生的情况，了解是否有录取的可能。请报出完整信息，包括姓名、高考裸分和加分。这三个都要报的。我们会针对个人给出相应信息。分数线现在肯定出不来，因为还没到最后投档的时候，请各位知悉。电话的人会比较多，如果占线请稍候再试试，也请打电话简明扼要，不要影响其他人打进来，谢谢！''',
'''2.  外省市考生须知：
（1） 请问在X X省的招生计划数是多少？
请查看您所在省份的招生计划书（俗称“大厚本”），在提前批次可以找到我校的招生计划数。各地招生计划数、历年分数线、具体录取流程请咨询当地本科招生小组，或参考各高中统订统发的由地方考试院出版的《招生目录》或《志愿填报手册》等出版物。

（2）高考出分后请及时反馈高考成绩（江苏省不需要反馈）：http://admission.shanghaitech.edu.cn/score_2016.php''',

'''（3）如有问题请及时与我校在的当地本科招生小组取得联系，联系方式表http://asa.shanghaitech.edu.cn/admission_detail.asp?id=136
各地招生计划数、历年分数线、具体录取流程及其他报考问题，均可直接拨打当地招生小组的电话咨询，仅在招生群内咨询没有办法回答。另外，请注意在开通时间内咨询。''',

'''重要提示：除江苏省有特殊政策，需要获得开放日加分方可报考外，全国其他地区考生可在提前批次第一志愿填报我校。上科大录取按高考分+校园开放日加分后的总分降序排序，择优录取。''']
            for i in range(len(t)):
                bot.reply_msg(msg, t[i] + '\n[{}/{} 我是机器人，被主人逼迫来这里发公告，请不要调戏我，谢谢~{}]'.format(i + 1, len(t), maimeng()))
                time.sleep(3)

#     if bot.gid_to_name(msg.from_uin) == '好好学习天天向上':
#         nowtime = datetime.datetime.now()
#         timedelta = nowtime - pretime[1]
#         if timedelta >= delta:
#             pretime[1] = nowtime
#             t = ['''1.  上海考生须知：
# 各位上海同学、家长：如果对综评有纠结的可以打电话到4009209393或者18930933479，报上考生的情况，了解是否有录取的可能。请报出完整信息，包括姓名、高考裸分和加分。这三个都要报的。我们会针对个人给出相应信息。分数线现在肯定出不来，因为还没到最后投档的时候，请各位知悉。电话的人会比较多，如果占线请稍候再试试，也请打电话简明扼要，不要影响其他人打进来，谢谢！''',
# '''2.  外省市考生须知：
# （1） 请问在X X省的招生计划数是多少？
# 请查看您所在省份的招生计划书（俗称“大厚本”），在提前批次可以找到我校的招生计划数。各地招生计划数、历年分数线、具体录取流程请咨询当地本科招生小组，或参考各高中统订统发的由地方考试院出版的《招生目录》或《志愿填报手册》等出版物。

# （2）高考出分后请及时反馈高考成绩（江苏省不需要反馈）：http://admission.shanghaitech.edu.cn/score_2016.php''',

# '''（3）如有问题请及时与我校在的当地本科招生小组取得联系，联系方式表http://asa.shanghaitech.edu.cn/admission_detail.asp?id=136
# 各地招生计划数、历年分数线、具体录取流程及其他报考问题，均可直接拨打当地招生小组的电话咨询，仅在招生群内咨询没有办法回答。另外，请注意在开通时间内咨询。''',

# '''重要提示：除江苏省有特殊政策，需要获得开放日加分方可报考外，全国其他地区考生可在提前批次第一志愿填报我校。上科大录取按高考分+校园开放日加分后的总分降序排序，择优录取。''']
#             for i in range(len(t)):
#                 bot.reply_msg(msg, t[i] + '\n[{}/{} 我是机器人，被主人逼迫来这里发公告，请不要调戏我，谢谢~{}]'.format(i + 1, len(t), maimeng()))
#                 time.sleep(3)

@on_private_message(name="faq")
def remove(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    # t = try_faq_p(msg.content, bot)
    # if t:
    #     t = filter_tags(t)
    #     t += '\n----\n{}我是上科大GeekPie机器人。加好友私聊提供更多信息问答服务。'.format(maimeng())
    #     bot.reply_msg(msg, t)
