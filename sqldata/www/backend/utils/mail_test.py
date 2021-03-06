#!/usr/bin/python
#-\*-coding: utf-8-\*-
import smtplib
from email.mime.text import MIMEText
import datetime
import json
import urllib.request
import time

class Ding(object):

    ding_api = "https://oapi.dingtalk.com/robot/send?access_token=dc6912a5a787a6d28d6a30c3775d4f8f674db6215d77a58a2e7b9d70ddc33e78"  # 设置钉钉机器人api
    see_addr = 'https://sqlaudit.julive.com'  # see项目访问地址
    @classmethod
    def print_log(cls,log):
        file_obj = open('/home/test.log', 'a+')
        log_time = time.strftime(
            '[%Y-%m-%d %H:%M:%S]',
            time.localtime(time.time()))  # 转化时间格式
        file_obj.write("%s\n" % (str(log)))
        file_obj.close()    # 记得close()
    @classmethod
    def get_desc(cls, action_type):
        desc_map = {
            '--enable-check': '提交',
            '--enable-execute': '执行',
            'approve': '审批',
            'disapprove': '驳回',
            'reject': '放弃',
            'rollback': '回滚'
        }
        return desc_map.get(action_type)

    @classmethod
    def get_ding_template(cls,to_list, personnel, sqlid, note, action_type, sqlcontent, dbname,atuser=[]):
        title = '{} SQL工单-{}'.format(cls.get_desc(action_type), sqlid)
        sql_html = ''
        for s in sqlcontent[0:1024].split(';'):
            if s:
                sql_html = sql_html + '\n > ' + s + ';'
        cls.print_log('开始')
        cls.print_log(len(atuser))
        if len(atuser) >=1:
            content_html = "@{} \n >{} {} [查看详情]({}/inceptionsql/{})\n >备注：{} 数据库（生产环境）：{} ".format(atuser[0],personnel, title, cls.see_addr, sqlid, note, dbname)
            my_data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "SQL工单通知",
                    "text": content_html + sql_html
                },
                "at": {
                    "atMobiles": atuser, 
                    "isAtAll": False
                }
            }
        else:
            content_html = "#### {} {} [查看详情]({}/inceptionsql/{})\n >备注：{} 数据库（生产环境）：{} ".format(personnel, title, cls.see_addr, sqlid, note, dbname)
            my_data = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": "SQL工单通知",
                        "text": content_html + sql_html
                    },
                    "at": {
                        "isAtAll": False
                    }      
            }
        # if len(sqlcontent) > 1024:
        #     sql_html = sql_html  + '#### 略... ...（内容较多，可查看详情）'           
        return my_data

    @classmethod
    def sendding(cls,to_list, personnel, sqlid, note, action_type, sqlcontent, dbname,atuser=[]):
        content = cls.get_ding_template(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname,atuser)
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        sendData = json.dumps(content)
        sendDatas = sendData.encode("utf-8")
        try:
            request = urllib.request.Request(url=cls.ding_api, data=sendDatas, headers=header)
            opener = urllib.request.urlopen(request)
            return True
        except Exception as e:
            print(e)
            return False
class Mail(object):

    smtp_host = "smtp.exmail.qq.com"  # 设置服务器
    smtp_port = 465  # SMTP协议默认端口是25
    mail_user = "system@comjia.com"  # 用户名
    mail_pass = "RfUvW2cgdCCTkxYe"  # 授权码
    see_addr = 'http://test.sqlaudit.julive.com'  # see项目访问地址

    @classmethod
    def get_desc(cls, action_type):
        desc_map = {
            '--enable-check': '提交',
            '--enable-execute': '执行',
            'approve': '审批',
            'disapprove': '驳回',
            'reject': '放弃',
            'rollback': '回滚'
        }
        return desc_map.get(action_type)

    @classmethod
    def get_mail_template(cls, to_list, action_type, sqlid, sqlcontent, personnel, note, dbname):
        to_list.append(cls.mail_user)
        title = '{} SQL工单-{}'.format(cls.get_desc(action_type), sqlid)
        sql_html = ''
        for s in sqlcontent[0:1024].split(';'):
            if s:
                sql_html = sql_html + '<div>' + s + ';' + '</div>'
        content_html = "<span style='margin-right:20px'>{} {}</span> <a href='{}/inceptionsql/{}'>【查看详情】</a> <p>备注：{}</p> <p>数据库（生产环境）：{} </p>".format(personnel, title, cls.see_addr, sqlid, note, dbname)
        if len(sqlcontent) > 1024:
            sql_html = sql_html + '<div>' + '略... ...（内容较多，可查看详情）' + '</div>'
        return title, content_html, sql_html, to_list

    @classmethod
    def send(cls, to_list, personnel, sqlid, note, action_type, sqlcontent, dbname,atuser=[]):  # to_list：收件人；sub：主题；content：邮件内容
        title, content_html, sql_html, to_list = cls.get_mail_template(to_list, action_type, sqlid, sqlcontent, personnel, note, dbname)
        msg = MIMEText(content_html + sql_html, _subtype='html', _charset='utf-8')  # 创建一个实例，这里设置为html格式邮件
        msg['Subject'] = '{} {} [{}]'.format(personnel, title, note)  # 设置主题
        msg['From'] = cls.mail_user
        msg['To'] = ";".join(to_list)
        try:
            Ding.sendding(to_list, personnel, sqlid, note, action_type, sqlcontent, dbname,atuser)
            smtp = smtplib.SMTP_SSL(cls.smtp_host, cls.smtp_port)
            smtp.login(cls.mail_user, cls.mail_pass)  # 登陆服务器
            smtp.sendmail(cls.mail_user, to_list, msg.as_string())  # 发送邮件
            smtp.quit()
            return True
        except Exception as e:
            print(e)
            return False

print(Mail.send(['904208360@qq.com'], 'zqf', 1234, '56565', 'approve','测试邮件', 'v9',[]))
