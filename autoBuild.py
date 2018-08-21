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
import emailUtil

import paramiko
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

#sftp
import sftp
from sftp import *

import email
from emailUtil import *

#文件地址


plist_path = "/Users/admin/Documents/autoConfig.plist"
uploadPlist_path = "/Users/admin/Documents/UploadConfig.plist"
email_Path = "/Users/admin/Documents/emailConfig.plist"

save_path = "/Users/admin/Documents/工作/包"
ipa_filename = ""



 #ftp配置
def ftpconnect(i,item):
    print(item)
    ftp_server = item["ftpServer"]
    username = item["userName"]
    password = item["passWord"]
    ftp = FTP()
    ftp.set_debuglevel(2)
    ftp.connect(ftp_server, 22)
    ftp.login(username, password)



#新建保存目录
def creat_folder(string):
	folderPath = save_path+"/"+string
	folderArchivePath = save_path+"/"+string+"/Archive"
	folderIpaPath = save_path+"/"+string+"/IPA"
	print(folderPath)
	if os.path.exists(folderPath) == False:
		os.makedirs(folderPath)
	if os.path.exists(folderArchivePath) == False:
		os.makedirs(folderArchivePath)
	if os.path.exists(folderIpaPath) == False:
		os.makedirs(folderIpaPath)

# 清理项目
def clean_project(i,item):
    print("** PACKROBOT START **")
    project_path = item["projectPath"]
    os.system('cd %s;xcodebuild clean' % project_path) # clean 项目
def rm_project_build(i,item):
    print("** REMOVE Build START **")
    project_path = item["projectPath"]
    os.system('rm -r %s/build' % project_path)
# archive项目
def build_project(i,item):
    project_name=item["name"]#工程名
    scheme=item["scheme"]#scheme
    project_type=item["projectType"]#工程类型 pod工程 -workspace 普通工程 -project
    configuration=item["configuration"] #编译模式 Debug,Release
    project_path=item["projectPath"]#项目根目录
    folderArchivePath = save_path+"/"+i+"/Archive"
    print("+++++++++++++++++++++++++++++++")
    print(folderArchivePath)
    archivePath=folderArchivePath#打包后存储目录
    mobileprovision_uuid=item["mobileprovisionUuid"]#mobileprovision uuid
    signing_certificate=item["signingCertificate"]#证书名称
    if project_type == "-workspace" :
        project_suffix_name = "xcworkspace"
    else :
        project_suffix_name = "xcodeproj"
    os.system ('cd %s;xcodebuild archive %s %s.%s -scheme %s -configuration %s -archivePath %s/%s.xcarchive CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" || exit' %   (project_path,project_type,project_name,project_suffix_name,scheme,configuration,folderArchivePath,project_name,signing_certificate,mobileprovision_uuid))
# 导出ipa包到自动打包程序所在目录
def exportArchive_ipa(i,item):
    global ipa_filename
    project_name=item["name"]#工程名
    folderArchivePath = save_path+"/"+i+"/Archive"#archive存储目录
    folderIpaPath = save_path+"/"+i+"/IPA"#ipa存储目录
    ipa_filename = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    ipa_filename = project_name + "_" + ipa_filename;#存储文件夹名
    exportOptionPath = item["exportOptionPath"]
    os.system ('xcodebuild -exportArchive -archivePath %s/%s.xcarchive -exportPath %s/%s -exportOptionsPlist %s' %(folderArchivePath,project_name,folderIpaPath,ipa_filename,exportOptionPath))
    return folderIpaPath+"/"+ipa_filename


#ftp上传
def uploadfile(i,item,appName,ipaPath):
    appPath = ipaPath
    #检测是否apps
    if os.path.exists("%s/Apps"%appPath):
        appPath = appPath+"/Apps"
        print(appPath)
    #拿出ipa
    if os.path.exists("%s/%s.ipa" % (appPath,appName)):
        remotepath = "/app/web/download/EQS/iPad/Test"
        ftp = ftpconnect(i,item)
        bufsize = 1024
        appPath = appPath+"/"+appName+".ipa"
        fp = open(appPath, 'rb')
        print(appPath)
        ftp.storbinary('STOR ' + remotepath, fp, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        ftp.quit()
    else:
        print("没有找到ipa文件")

def sftp(i,item,appName,ipaPath):
    remotefile = item["remotePath"]
    remotefile = remotefile+"/"+appName+".ipa"
    appPath = ipaPath
    #检测是否apps
    print("appPath        "+appPath)
    if os.path.exists("%s/Apps"%appPath):
        appPath = appPath+"/Apps"
        print(appPath)
    appPath = appPath+"/"+appName+".ipa"
    linux = Linux(item["ftpServer"], item["userName"], item["passWord"])
    # 将远端的xxoo.txt get到本地，并保存为ooxx.txt
    print("remotefile     "+remotefile)
    print("appPath        "+appPath)
    #上传刷新
    linux.sftp_put(appPath,remotefile)
    # # 将本地的xxoo.txt put到远端，并保持为xxoo.txt
    # host.sftp_put(appPath, remotefile)

#发送邮件
def emailSend(dic):
	email=EmailUtil(dic)
	email.send_mail()

if __name__ == '__main__':
	reload(sys) 
	sys.setdefaultencoding("utf-8")
	plist=plistlib.readPlist(plist_path)
	uploadPlist=plistlib.readPlist(uploadPlist_path)
	emailPlist=plistlib.readPlist(email_Path)
	print(uploadPlist)
	for i,value in plist.items():
		creat_folder(i)
		clean_project(i,value)
		build_project(i,value)
		ipaPath = exportArchive_ipa(i,value)
		rm_project_build(i,value)
		print("exportArchive_ipa path ~~~~~~~~~~~~"+ipaPath)
		#上传逻辑
		for iup,valueup in uploadPlist.items():
			print(uploadPlist)
			if(iup=="SFTP"):
				sftp(iup,valueup,value["name"],ipaPath)
			emailSend(emailPlist)



