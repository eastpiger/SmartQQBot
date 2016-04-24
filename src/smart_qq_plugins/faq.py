# coding: utf-8
import json
import urllib
import logging
import time
import os
import random
from random import randint
import re
from smart_qq_bot.signals import on_group_message, on_private_message

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
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
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
    if bot.gid_to_name(msg.from_uin) == '好好学习天天向上':
        t = try_faq(msg.content, bot)
        if t:
            t = filter_tags(t)
            t += '\n----\n{}我是上科大GeekPie机器人。加好友私聊提供更多信息问答服务。'.format(maimeng())
            while len(t) > 400:
                bot.reply_msg(msg, t[:400])
                t = t[400:]
                time.sleep(3)
            bot.reply_msg(msg, t)
    if bot.gid_to_name(msg.from_uin) == '上科大本科招生咨询群':
        t = try_faq(msg.content, bot)
        if t:
            t = filter_tags(t)
            t += '\n----\n{}我是上科大GeekPie机器人。加好友私聊提供更多信息问答服务。'.format(maimeng())
            while len(t) > 400:
                bot.reply_msg(msg, t[:400])
                t = t[400:]
                time.sleep(3)
            bot.reply_msg(msg, t)


@on_private_message(name="faq")
def remove(msg, bot):
    """
    :type bot: smart_qq_bot.bot.QQBot
    :type msg: smart_qq_bot.messages.GroupMsg
    """
    t = try_faq_p(msg.content, bot)
    if t:
        t = filter_tags(t)
        t += '\n----\n{}我是上科大GeekPie机器人。加好友私聊提供更多信息问答服务。'.format(maimeng())
        bot.reply_msg(msg, t)
