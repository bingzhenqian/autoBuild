#coding:utf-8

import plistlib
import os
import sys
import time
import hashlib
from ftplib import FTP

import time
import tarfile

import smtplib
import email

import paramiko
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
#文件地址
# 定义一个类，表示一台远端linux主机
pgyer_appQRCodeURL = "http://download.autostreets.com/"
ERCodeImage_path = "/Users/admin/Documents/django/python网络编程/工作/自动化打包/biplisttest/code.png"
class EmailUtil(object):
    def __init__(self,config):
        self.from_addr = config["fromAddr"]
        self.to_addr = config["toAddr"]
        self.pass_word=config["passWord"]
        self.smtp_server=config["smtpServer"]
        self.app_name=config["appName"]
        
    # 地址格式化
    def _format_addr(self,s):
        name,addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    # 发邮件
    def send_mail(self):
        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = self.from_addr
        msgRoot['To'] = ",".join(self.to_addr)
        msgRoot['Subject'] = Header(self.app_name + " iOS 客户端版本构建完成, 构建时间:" + time.strftime('%Y年%m月%d日%H:%M:%S',time.localtime(time.time())), 'utf-8').encode()
        msgText = MIMEText(self.app_name + " iOS客户端已经打包完毕，请扫描附件中的二维码或前往 " + pgyer_appQRCodeURL + " 下载测试！如有问题，请联系钱谢谢!", 'plain', 'utf-8')
        msgRoot.attach(msgText)

        # 添加图片类型附件
        local_path_filename = os.path.expanduser(ERCodeImage_path)
        if(os.path.exists(local_path_filename)) :
            fpath,fname = os.path.split(local_path_filename)
            with open(local_path_filename, 'rb') as imageFile:
                mime = MIMEBase('image', 'png', filename = fname)
                mime.add_header('Content-Disposition', 'attachment', filename=fname)
                mime.add_header('Content-ID', '<0>')
                mime.add_header('X-Attachment-Id', '0')
                mime.set_payload(imageFile.read())
                encoders.encode_base64(mime)
                msgRoot.attach(mime)

        server = smtplib.SMTP(self.smtp_server, 25)
        server.set_debuglevel(1)
        server.login(self.from_addr, self.pass_word)
        server.sendmail(self.from_addr,self.to_addr, msgRoot.as_string())
        server.quit()

if __name__ == '__main__':
    reload(sys) 
    sys.setdefaultencoding("utf-8")






