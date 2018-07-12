#1搭建网络连接
from socket import *
import os
import sys

#refer from:https://blog.csdn.net/Black_spider1/article/details/80698074

def do_login(s,user,name,addr):
	if (name in user) or name =='管理员':
		s.sendto('该用户存在'.encode,addr)
		return
	s.sendto(b'OK',addr)
	#通知所有人
	msg = '\n欢迎 %s 进入聊天室'%name
	for i in user:
		s.sendto(msg.encode(),user[i][0])
	#将用户插入字典
	hidden_flag = False
	user[name] = [addr,hidden_flag]

	#print('登录')

def do_chat(s,user,name,text):
	msg = '\n%-4s 说:%s'%(name,text)
	if text == "hide":
		user[name][1] = True
		return
	#发给所有人,除了自己
	for i in user:
		if i != name:
			s.sendto(msg.encode(),user[i][0])
	#print('聊天')

def do_quit(s,user,name):
	del user[name]
	msg = '\n'+ name + '离开了聊天室'
	for i in user:
		s.sendto(msg.encode(),user[i][0])
	#print('退出')

def do_p2pChat(s,user,name,text):
	send_text = " ".join(text.split(" ")[1:])
	msg = '\n%-4s 说:%s'%(name,send_text)
	target_username = text.split(" ")[0]
	target_user = user[target_username][0]
	if user[target_username][1] == True:
		feedback_msg = "\nuser %s is in the offline state" %(target_username)
		s.sendto(feedback_msg.encode(),user[name][0])
	else:
		s.sendto(msg.encode(),target_user)

#接收客户端请求并处理
def do_child(s):
	#用于存储用户{'z':(172.60.50.51,8956)}
	#可变类型,修改可被影响
	user = {}
	#循环接收个个客户端请求并处理
	while True:
		msg,addr = s.recvfrom(1024)
		msgList = msg.decode().split(' ')
		#判断请求类型进行处理
		if msgList[0] == 'L':
			do_login(s,user,msgList[1],addr)
		elif msgList[0] == 'C':
			do_chat(s,user,msgList[1],' '.join(msgList[2:]))
		elif msgList[0] == 'Q':
			do_quit(s,user,msgList[1])
		elif msgList[0] == 'S':
			do_p2pChat(s,user,msgList[1]," ".join(msgList[2:]))



#发送管理员消息
def do_parent(s,addr):
	while True:
		msg = input('管理员消息:')
		msg = 'C 管理员 ' + msg
		s.sendto(msg.encode(),addr)


#1创建套接字,创建连接,创建父子进程
def main():
	#server address
	ADDR = ('0.0.0.0',10010)
	s = socket(AF_INET,SOCK_DGRAM)
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	s.bind(ADDR)

#创建父子进程,并且防止僵尸进程
	pid = os.fork()

	if pid < 0:
		sys.exit('创建进程失败')
	elif pid == 0:
		#创建二级子进程
		pid0 = os.fork()
		if pid0 < 0:
			sys.exit('创建失败')
		elif pid0 ==0 :
			#执行子进程功能
			do_child(s)
		else:
			os._exit(0)
	else:
		os.wait()
		#执行父进程功能
		do_parent(s,ADDR)

if __name__=='__main__':
	main()

