import re
import gzip
import zlib
import urllib.request as request
import urllib
import datetime
import http.cookiejar
import time
import copy
import os
import sys
import urllib.robotparser as rbp
import threading
import queue
import tkinter.filedialog as tkFileDialog
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter.ttk import *
import webbrowser
import configparser
import winreg
import base64
import shelve
import dbm
from bs4 import BeautifulSoup

"""
修正了爬取链接之后不能使用配置管理器的bug
增加了自动打开文件的功能
"""

version = "V1.1.1"
position_global = sys.path[0]

os.chdir(position_global)

__headers__ = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding': 'deflate, gzip',
'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
'Cache-Control': 'no-cache',
'Connection': 'Keep-Alive','Pragma':'no-cache'}

has_redirect = []
unable_list = {}
console_num = 0
console_log = ""
clear = False

class ConfigControlPanel:
	def __init__(self):
		master = Toplevel(root)
		self.master = master
		master.title("配置文件管理器")
		master.geometry("620x300")
		master.resizable(False, False)
		master.iconbitmap("icon.ico")
		self.show()
	def update_button(self):
		config_Treeview = self.config_Treeview
		if len(config_Treeview.get_children()) == 1:
			self.remove_data_Button['state'] = "disabled"
		else:
			self.remove_data_Button['state'] = "normal"
	def show(self):
		master = self.master
		self.data_Title = data_Title = ("名称","地址","密码","存储位置")
		config_Treeview = Treeview(master,columns=data_Title,show='headings',selectmode='extended')
		config_scrollY = Scrollbar(master,orient=VERTICAL,command=config_Treeview.yview)
		config_scrollY = Scrollbar(master,orient=VERTICAL)
		self.config_Treeview= config_Treeview
		self.add_Button()
		self.show_data()
	def show_data(self):
		config_Treeview = self.config_Treeview
		config_Treeview.grid(row=1,column=1,columnspan=3,sticky=W)
		for project in config_Treeview.get_children():
			config_Treeview.delete(project)
		if os.path.isfile("config.conf"):
			cf = configparser.SafeConfigParser()
			self.cf = cf
			try:
				cf.read("config.conf")
			except:
				messagebox.showerror("错误","无法读取配置文件，请检查。")
				self.master.destroy()
				return False
		else:
			messagebox.showinfo("提示","不存在配置文件，第一次使用请先保存一份默认配置")
			self.master.destroy()
			return False
		data_Title = self.data_Title
		self.swing = swing = cf.sections()
		data = []
		for item in swing:
			all_info = (dict(cf.items(item)))
			data.append(tuple([item,all_info['url_top'],all_info['key_url'],all_info['position']]))
		for item in data_Title:
			if item == "名称":
				config_Treeview.heading(item,text=item.title())
				config_Treeview.column(item,width=78)
				continue
			config_Treeview.heading(item, text=item.title())
			config_Treeview.column(item,width=180)
		for item in data:
			config_Treeview.insert('', 'end', values=item)
		self.update_button()
	def add_Button(self):
		master = self.master
		self.add_data_Button = Button(master,text="存储配置",command=self.add_data)
		self.remove_data_Button = Button(master,text="移除配置",command=self.remove_data)
		self.load_data_Button = Button(master,text="载入配置",command=self.load_data)
		self.add_data_Button.grid(row=2,column=1,pady=20)
		self.remove_data_Button.grid(row=2,column=2)
		self.load_data_Button.grid(row=2,column=3)
		self.update_button()
	def remove_data(self):
		cf = self.cf
		config_Treeview = self.config_Treeview
		try:
			select_li = config_Treeview.selection()[0]
		except:
			return False
		buttun_data = (select_li,config_Treeview.item(config_Treeview.focus())['values'][0])
		if buttun_data[1] == "default":
			messagebox.showerror("错误","不能移除默认配置！")
			return False
		confirm_del = messagebox.askyesno("确认","您确认要删除 %s 的配置文件吗？" % buttun_data[1])
		if confirm_del:
			try:
				cf.remove_section(buttun_data[1])
				open_file = open("config.conf","w")
			except:
				messagebox.showerror("错误","删除失败！")
				return False
			else:
				messagebox.showinfo("成功","已成功删除 %s 配置" % buttun_data[1])
				cf.write(open_file)
			config_Treeview.delete(buttun_data[0])
		self.update_button()
		self.swing = self.cf.sections()
	def load_data(self):
		config_Treeview = self.config_Treeview
		try:
			select_li = config_Treeview.selection()[0]
		except:
			return False
		buttun_data = (select_li,config_Treeview.item(config_Treeview.focus())['values'][0])
		try:
			use_config(load_config(buttun_data[1]))
		except:
			messagebox.showerror("失败","载入配置文件失败！")
			return False
		else:
			messagebox.showinfo("成功","载入 %s 配置成功！" % buttun_data[1])
		self.update_button()
	def add_data(self):
		config_Treeview = self.config_Treeview
		Entry_box = self.get_input_name(config_Treeview)
		self.master.wait_window(self.top)
		try:
			get_save_name = self.value
		except:
			pass
		if get_save_name in self.swing:
			messagebox.showerror("错误","存在 %s 配置，请先移除它。" % get_save_name)
			return False
		try:
			save_config(get_save_name)
		except:
			messagebox.showerror("错误","保存配置失败！")
		self.show_data()
		self.update_button()
	def get_input_name(self,parent):
		top = self.top = Toplevel(parent)
		top.title("存储到配置文件")
		top.geometry("255x107")
		top.resizable(False, False)
		top.iconbitmap("icon.ico")
		Label(top,text="在此键入您要保存配置的名称：").grid(row=1,column=1,columnspan=2,padx=20,pady=5)
		self.input_entry_in = StringVar()
		self.input_entry = Entry(top,textvariable=self.input_entry_in)
		self.input_entry.grid(row=2,column=1,columnspan=2,padx=20,pady=5)
		Button(top,text="确定",command=self.echo_value).grid(row=3,column=1,pady=5,padx=20)
		Button(top,text="取消",command=self.cancel).grid(row=3,column=2,padx=20)
		self.input_entry.focus_set()
	def echo_value(self):
		value = self.input_entry_in.get()
		try:
			assert (1 < len(value) < 11)
			assert (value.isalpha())
		except:
			messagebox.showerror("错误","仅允许长度2~9之内的字母组合作为配置名！")
		else:
			self.value = value
			self.cancel()
	def cancel(self):
		self.top.destroy()
	
def check_software_update():
	oper = build_head("Chrome")
	check_update_url = "http://www.nfishs.com/BaiduSubmitUp?version=%s" % version
	check_software_update_Button['state'] = "disabled"
	conn = oper.open(check_update_url)
	data_sendback = conn.read()
	try:
		if dict(conn.headers.items())["Content-Encoding"] == "gzip":
			data_sendback = gzip.decompress(data_sendback)
		elif dict(conn.headers.items())["Content-Encoding"] == "deflate":
			data_sendback = zlib.decompress(data,-zlib.MAX_WBITS)
	except:
		pass
	data_sendback = data_sendback.decode("UTF-8",'ignore')
	if not (len(data_sendback) == 0):
		data_sendback = data_sendback.replace("\\","")
		data_sendback = (eval(data_sendback))
	else:
		data_sendback = ""
	if len(data_sendback) != 0:
		ask = messagebox.askyesno("提示","发现最新版本：%s 当前版本：%s ，是否下载？" % (data_sendback['Version'],version))
		if ask:
			webbrowser.open(data_sendback['Download'])
	else:
		messagebox.showinfo("提示","暂未发现新版本！")
	check_software_update_Button['state'] = "normal" 

def print_active():
	while True:
		time.sleep(1)
		print (threading.activeCount())

def stop_spider():
	global clear
	ask_stop = messagebox.askyesno("提示","您确定要停止当前进行的爬取任务吗？")
	if not ask_stop:
		return False
	clear = True
	insert_console_end("Stopped the task.\n")
	run_spider_button['state'] = "normal"
	# threading.Thread(target=print_active).start()

def insert_console_end(content):
	if not isinstance(content,str):
		return False
	cmd.insert(END,content)
	global console_num
	global console_log
	console_num += 1
	console_log += content
	if console_num >= 150:
		clear_cmd()
		console_num = 0
	cmd.see(END)

def write_error_links(unable_list,url_top):
	position = position_in.get()
	if len(position) == 0:
		position = position_global
	os.chdir(position)
	time_write = str(datetime.datetime.now())[0:-7]
	try:
		file_open = open("wrong-link.txt","a")
	except:
		messagebox.showerror("错误","无法创建死链列表文件，请检查！")
		return False
	file_open.write(u"\nWorng Links ---- " + url_top + " : " + time_write + "\n")
	for links in unable_list.keys():
		file_open.write(links +" : "+ unable_list[links]+"\n")
	file_open.close()
	return True

def start_update():
	update_th = threading.Thread(target=get_update)
	update_th.setDaemon(True)
	update_th.start()

def get_password():
	password = key_url_in.get()
	regx = "http://data.zz.baidu.com/urls\?site=(.*)&token=(.*)"
	regx = re.compile(regx)
	if not regx.match(password):
		url_top = get_url_top()
		regx_div = re.compile(r"(http|https)://(.*)")
		url_top = regx_div.match(url_top).group(2)
		password = "http://data.zz.baidu.com/urls?site=%s&token=%s" % (url_top,password)
	if len(password) == 0:
		messagebox.showerror("错误","请输入提交密码！")
		return False
	if original_in.get():
		password += "&type=original"
	return password

def get_update():
	resource = []
	try:
		os.chdir(position_in.get())
	except:
		messagebox.showerror("警告","指定的位置不正确或无法访问，请检查！")
		os.chdir(position_global)
		return False
	url_top = base64.urlsafe_b64encode(get_url_top().strip("/").encode()).decode()
	if (not os.path.isfile(url_top+".dat")) or (not os.path.isfile(url_top+".dir")):
		messagebox.showerror("警告","未查找到数据文件，请检查目录或先抓取数据！")
		os.chdir(position_global)
		return False
	try:
		open_db = shelve.open(url_top)
	except:
		messagebox.showerror("错误","您所指定的文件位置不能打开文件，请检查！")
	insert_console_end("\nOpening datafile and finding update data....\n")
	for i in open_db.keys():
		resource.append(int(i))
	resource.sort()
	if len(resource) < 2:
		messagebox.showinfo("警告","您的文件中只有一次记录，请先更新！（提醒：一天最好只提交更新一次）")
		os.chdir(position_global)
		return False
	if len(resource) >= 8:
		insert_console_end("\nClearing old data.....")
		for record in resource[0:-4]:
			del open_db[str(record)]
	time_name = datetime.datetime.now().date().strftime("%Y%m%d")
	if str(resource[-1]) != time_name:
		value = messagebox.askyesno("提醒","您当前的记录文件中未找到今日记录，有可能提交旧数据，是否提交？")
		if not value:
			os.chdir(position_global)
			return False
	old_data = open_db[str(resource[-2])]
	new_data = open_db[str(resource[-1])]
	if "HAS_UPDATED" in new_data:
		update_choice = messagebox.askyesno("警告","今日数据已提交过，可能会重复提交，是否提交？")
		if not update_choice:
			os.chdir(position_global)
			return False
	try:
		new_data.remove("HAS_UPDATED")
		old_data.remove("HAS_UPDATED")
	except:
		pass
	find_new = list(set(new_data) - set(old_data))
	if len(find_new) == 0:
		insert_console_end('\nNo new record founded, Pass.....')
		messagebox.showinfo('提醒','您的文件记录中未找到更新数据。')
		os.chdir(position_global)
		return False
	insert_console_end('Already found %s new record. Sending.....\n' % str(len(find_new)))
	try:
		find_new.remove("HAS_UPDATED")
	except:
		pass
	for url_send in find_new:
		insert_console_end("update : "+url_send+"\n")
	password = get_password()
	if not password:
		os.chdir(position_global)
		return False
	send_update(find_new,password)
	has_updated = open_db[str(resource[-1])]
	has_updated.append("HAS_UPDATED")
	open_db[str(resource[-1])] = has_updated
	open_db.close()

def query_remain():
	password =get_password()
	if not password:
		return False
	query_thread = threading.Thread(target=send_update,name="thread_query",args=("",password,True))
	query_thread.start()
	query_Button['state'] = "disabled"

def send_update(para,password,Query=False):
	error_zh = {"token is not valid":"准入密钥填写错误，请检查！",
	"site error":"站点未在站长平台验证，请检查！",
	"only 2000 urls are allowed once":"每次最多只能提交2000条链接！",
	"over quota":"提交超过每日配额了，超配额后再提交都是无效的！",
	"not found":"接口地址填写错误！",
	"internal error, please try later":"服务器偶然异常，请重试！"}
	header = {'User-Agent': 'curl/7.12.1', 'Content-type': 'text/plain', 'Host': 'http://data.zz.baidu.com'}
	para = '\n'.join(para).encode()
	run_baidu_button['state'] = "disabled"
	try:
		req = request.Request(password,data=para)
	except ValueError:
		show_update_back("请检查您的提交密码是否正确",False)
		run_baidu_button['state'] = "normal"
		return False
	except:
		show_update_back("请检查提交地址正确性与网络情况",False)
		run_baidu_button['state'] = "normal"
		return False
	for k,v in header.items():
		req.add_header(k,v)
	try:
		response = request.urlopen(req)
	except urllib.error.HTTPError as error:
		response = eval(error.read())
		run_baidu_button['state'] = "normal"
		error_message = error_zh[response['message']]
		show_update_back(error_message,False)
		return False
	else:
		run_baidu_button['state'] = "normal"
		response = eval(response.read())
		if Query:
			message_Query = """查询结果：
今日剩余可推送条数:%s""" % str(response['remain'])
			show_update_back(message_Query,"Query")
			query_Button['state'] = "normal"
			return True
		message_success = """推送成功！详细信息：
本次成功推送条数:%s
今日剩余可推送条数:%s
		""" % (str(response['success']),str(response['remain']))
		show_update_back(message_success,True)
		
def show_update_back(message,success=True):
	if success:
		messagebox.showinfo("成功",message)
	elif success == "Query":
		messagebox.showinfo("提示",message)
	else:
		messagebox.showerror("错误",message)

def check_proxy():
	# proxy = False
	key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
		r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
		0, winreg.KEY_ALL_ACCESS)
	# if winreg.QueryValueEx(key,"ProxyEnable")[0]:
	# 	proxy = winreg.QueryValueEx(key,"ProxyServer")[0]
	# else:
	try:
		if winreg.QueryValueEx(key,"AutoConfigURL")[1]:
			proxy = winreg.QueryValueEx(key,"AutoConfigURL")[0]
	except:
		proxy = False
	winreg.CloseKey(key)
	return proxy

def start_GUI_spider():
	global url_top
	names = get_config()
	if not names:
		return False
	key_url = names["key_url"]
	timeout = names["timeout"]
	threadNum = names["threadNum"]
	self_site = names["self_site"]
	url_top = names["url_top"]
	writen_file = names["writen_file"]
	explorer = names["explorer"]
	position = names["position"]
	use_proxy = names["use_proxy"]
	original = names["original"]
	if not url_top.startswith("http://") and not url_top.startswith("https://") or len(url_top) == 0:
		messagebox.showerror("错误","URL不符合要求，请检查")
		return False
	run_spider_button['state'] = "disabled"
	oper = build_head(explorer,use_proxy)
	th_th_sp = threading.Thread(target=thread_run_spider,args=(url_top,self_site,timeout,oper,threadNum,writen_file,position))
	th_th_sp.setDaemon(True)
	insert_console_end("Starting catch URL, please wait thread start, it may take a while.\n")
	th_th_sp.start()
	stop_Button['state'] = "normal"

def use_config(names):
	key_url_in.set(names["key_url"])
	timeout_in.set(names["timeout"])
	self_site_in.set(names["self_site"])
	url_top_in.set(names["url_top"])
	writen_file_in.set(names["writen_file"])
	explorer_in.set(names["explorer"])
	position_in.set(names["position"])
	use_proxy_in.set(names["use_proxy"])
	original_in.set(names['original'])
	threadNum_in.set(names["threadNum"]+"线程")
	save_file()
	if names["self_site"]:
		self_site_in.set(True)

def load_config(name):
	names = {}
	names["key_url"] = ""
	names["timeout"] = "4"
	names["threadNum"] = "4"
	names["self_site"] = "1"
	names["url_top"] = ""
	names["writen_file"] = "1"
	names["explorer"] = "Chrome"
	names["position"] = ""
	names["use_proxy"] = "0"
	names["original"] = "1"
	if os.path.isfile("config.conf"):
		cf = configparser.SafeConfigParser()
		try:
			cf.read("config.conf")
		except:
			messagebox.showerror("错误","无法读取配置文件，请检查。")
			return False
		else:
			config_read = ['key_url','timeout','original','threadNum','self_site','url_top','writen_file','explorer','position']
			for i in config_read:
				try:
					names[i] = cf.get(name,i)
				except:
					messagebox.showerror("错误","配置文件损坏，使用默认配置")
					break
			return names
	else:
		return names

def get_url_top():
	url_top = url_top_in.get()
	regx = "(http|https)://.*"
	regx = re.compile(regx)
	if not regx.match(url_top):
		url_top = "http://" + url_top
	return url_top

def get_config():
	url_top = get_url_top()
	key_url = key_url_in.get()
	timeout = timeout_in.get()
	original = original_in.get()
	explorer = explorer_in.get()
	self_site = self_site_in.get()
	writen_file = writen_file_in.get()
	use_proxy = use_proxy_in.get()
	position = position_in.get()
	try:
		timeout = int(timeout)
		assert(0 < timeout <= 3600)
	except:
		messagebox.showerror("错误","超时时间设置错误，请检查。")
		return False
	if writen_file:
		if len(position) == 0:
			messagebox.showinfo("提示","您未选择存储的文件位置，文件会被默认保存在这个程序的路径下。")
			global position_global
			position = position_global
		if not os.path.isdir(str(position)):
			messagebox.showerror("错误","文件存储位设置错误，请检查。")
			return False
	try:
		threadNum = int(threadNum_in.get()[0])
		assert(1 <= threadNum <=8)
	except:
		messagebox.showerror("错误","线程数设置错误，请检查。")
		return False
	return {'url_top':url_top,'key_url':key_url,'timeout':timeout,'position':position,
	'threadNum':threadNum,'explorer':explorer,'self_site':self_site,'writen_file':writen_file,
	'original':original,'use_proxy':use_proxy}

def save_config(name="default"):
	config = get_config()
	os.chdir(position_global)
	if config:
		try:
			file_open = open("config.conf","a")
		except:
			messagebox.showerror("错误","无法创建config.conf文件，请检查权限。")
			return False
		else:
			if name == "default":
				try:
					cf = configparser.SafeConfigParser()
					cf.read("config.conf")
					cf.remove_section("default")
					cf.write(open("config.conf","w"))
				except:
					messagebox.showerror("错误","更新默认配置文件出错！")
					return False
			file_open.write("[%s]\n" % name)
			for item in config:
				file_open.write(str(item) + " = " + str(config[item]) + "\n")
			file_open.close()
			if name == "default":
				messagebox.showinfo("成功","写入到默认配置成功，下次启动将会载入当前配置。")
			else:
				messagebox.showinfo("成功","写入配置 %s 成功！" % name)

root = Tk()

def save_log():
	os.chdir(position_global)
	global console_log
	content = console_log
	if content and len(content) != 0:
		try:
			open_file = open("runtime.log","a")
		except:
			messagebox.showerror("错误","无法写入文件runtime.log，请检查权限.")
			return False
		else:
			time_write = str(datetime.datetime.now())[0:-7]
			open_file.writelines("\n"+time_write+" -- "+"LOG\n")
			open_file.writelines(content)
			open_file.close()
			messagebox.showinfo("成功","保存为runtime.log文件成功！")
	else:
		messagebox.showinfo("提示","控制台无输出！")

def clear_cmd(del_log_mem=False):
	try:
		cmd.delete(0.0,END)
		if del_log_mem:
			global console_log
			console_log = ""
	except TclError:
		pass

def CallFileDialog():
	position_in.set("")
	filepath = tkFileDialog.askdirectory()
	position_in.set(filepath)

def out_file(url_list):
	global url_top
	time_name = datetime.datetime.now().date().strftime("%Y%m%d")
	try:
		open_file = shelve.open(base64.urlsafe_b64encode(url_top.encode()).decode())
	except:
		messagebox.showerror("错误","现在不能写入数据到文件，请检查权限。")
		os.chdir(os.path.split(os.path.realpath(sys.argv[0]))[0])
		return False
	else:
		open_file[time_name] = url_list
		messagebox.showinfo("成功","文件写入成功！")
		open_file.close()
	finally:
		os.chdir(position_global)

def write_file(url_list,position=None):
	if not position:
		out_file(url_list)
	else:
		if not os.path.isdir(str(position)):
			try:
				os.makedirs(position)
			except:
				messagebox.showerror("错误","在您所指定的位置不能创建文件夹，请检查权限。")
				return False
			else:
				os.chdir(position)
				out_file(url_list)
		else:
			os.chdir(position)
			out_file(url_list)

def build_head(UA,use_proxy=True,headers=__headers__):
	cookie_jar = http.cookiejar.CookieJar()
	cookie_support = request.HTTPCookieProcessor(cookie_jar)
	User_Agent_IE = "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko"
	User_Agent_Chrome = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'
	if UA == "IE":
		headers['User-Agent'] = User_Agent_IE
	else:
		headers['User-Agent'] = User_Agent_Chrome
	proxy_handler = request.ProxyHandler({})
	if use_proxy:
		proxy_handler = request.ProxyHandler()
		try:
			regx_sys_proxy = re.compile(r"^(http|https)://(.*)?/")
			system_proxy = check_proxy()
			system_proxy = regx_sys_proxy.findall(system_proxy)[0][1]
		except:
			system_proxy = False
		if system_proxy:
			proxy_handler = request.ProxyHandler({'http:':"http://%s/" % system_proxy
				,'https:':"http://%s/" % system_proxy,'ftp':"ftp://%s/" % system_proxy})
	oper = request.build_opener(cookie_support,request.HTTPHandler,proxy_handler)
	request.install_opener(oper)
	header = []
	for key, value in headers.items():
		elem = (key, value)
		header.append(elem)
	oper.addheaders = header
	return oper

def catch_url(url,oper,timeout=4):
	global unable_list
	# print ((oper.handle_open['http'][0]).proxies)
	try:
		conn = oper.open(url,timeout=timeout)
		data = conn.read()
	except urllib.error.HTTPError as error:
		insert_console_end(("Error : "+url+" : "+str(error.code)+"\n"))
		unable_list[url] = str(error.code)
		return False
	except urllib.error.URLError as error:
		if str(error) == "<urlopen error timed out>":
			insert_console_end(("Error : "+url+" : "+"Timeout(%s)\n" % (str(timeout) + "s")))
		unable_list[url] = "Timeout"
		return False
	except ValueError as error:
		insert_console_end(("Error : " + str(error.with_traceback(None))+"\n"))
		return False
	except:
		insert_console_end("Unkonwn Error. Pass...\n")
		unable_list[url] = "Unkonwn Error"
		return False
	else:
		conn.close()
		try:
			if dict(conn.headers.items())["Content-Encoding"] == "gzip":
				return gzip.decompress(data),conn
			elif dict(conn.headers.items())["Content-Encoding"] == "deflate":
				return zlib.decompress(data,-zlib.MAX_WBITS),conn
		except:
			return data,conn

def find_url(data_sendback,self_site):
	url = []
	url_insert = url_top.strip("http://").strip("https://")
	soup = BeautifulSoup(data_sendback,"html.parser")
	http_protocol = "http://"
	for link in soup.find_all('a'):
		href = link.get("href")
		if href:
			if href.startswith("https://"):
				http_protocol = "https://"
			href = href.strip(" ")
			if (not href.startswith("javascript")) and (not "#" in href):
				if href.startswith("/"):
					href = http_protocol + url_insert + href
					url.append(href)
					continue
				if self_site:
					if href.startswith(http_protocol+url_insert):
						url.append(href)
	for link in url:
		if not (link.startswith("http") or link.startswith("https")):
			url.remove(link)
	url = list(set(url))
	return url

def check_url(url_list):
	global rb_check
	global url_top
	regx_check_url = r"^(http://)|(https://)(.*\.)+.*"
	check_url_in = re.compile(regx_check_url)
	url = copy.deepcopy(url_list)
	url_top = url_top.strip("/")
	check_media = re.compile(r"/?.*\.(.*)$")
	for url_tm in url_list:
		url_tm.strip('.')
		if url_tm.startswith("/"):
			url.remove(url_tm)
			url_tm = url_top + url_tm
			url.append(url_tm)
		if len(check_url_in.findall(url_tm)) == 0:
			url.remove(url_tm)
			continue
		out_of_url = check_media.findall(url_tm.split('/')[-1])
		if len(out_of_url) != 0:
			if not (out_of_url[-1] in ['html','htm','shtml']):
				url.remove(url_tm)
				continue
		if rb_check:
			if not rb_check.can_fetch("*",url_tm):
				try:
					url.remove(url_tm)
				except:
					pass
	return url

def find_meta(data_sendback):
	data_back = str(data_sendback[0])
	try:
		head_sendback = dict(data_sendback[1].headers.items())["Content-Type"]
		charset = head_sendback.split(";")[1].strip(" ").split("=")[1]
	except:
		charset = None
	regx_equiv = r'http-equiv="?(.*?)"'
	regx_equiv = re.compile(regx_equiv)
	try:
		equiv = regx_equiv.findall(data_back)[0].strip('"')
	except IndexError:
		equiv = None
	return [equiv,charset]

def redirect_url(data):
	global has_redirect
	regx_find_reurl = r'content="([0-9]+);url=(.*?)"'
	regx_find_reurl = re.compile(regx_find_reurl)
	redirect_info = regx_find_reurl.findall(str(data))
	redirect_timewait = redirect_info[0][0]
	redirect_target = redirect_info[0][1]
	if redirect_target in has_redirect:
		return False
	else:
		has_redirect.append(redirect_target)
		return redirect_timewait,redirect_target

def rm_robots(url_top):
	global rb_check
	rb_check = None
	try:
		rb_check = rbp.RobotFileParser()
		rb_check.set_url(url_top+"/robots.txt")
		rb_check.read()
	except:
		rb_check = None
		return False
	else:
		return True

def main_do(url,self_site,threadName,oper,timeout=4):
	url_static_for_time = url
	start_time = datetime.datetime.now()
	global has_redirect
	global url_top
	url_top = 'http://'+url.split('/')[2]+"/"
	insert_console_end(("Starting catch url in %s -- %s \n" % (url,"Thread : "+str(threadName))))
	data = catch_url(url,oper,timeout)
	if not data:
		try:
			del has_redirect
		except:
			pass
		return False
	meta = find_meta(data)
	data = data[0]
	if meta[0] != "refresh":
		if meta[1]:
			data = data.decode(meta[1],'ignore')
		else:
			try:
				data = data.decode()
			except:
				pass
		url = find_url(data,self_site)
		url = check_url(url)
		try:
			del has_redirect
		except:
			pass
		end_time = datetime.datetime.now()
		insert_console_end((url_static_for_time + " Done, Use Time: %s" % str(round((end_time-start_time).total_seconds(),2)) + ' s\n'))
		return url
	else:
		redirect_info = redirect_url(data)
		if not redirect_info:
			insert_console_end((url+" have Redirect loop. Skip this url.\n"))
			return False
		insert_console_end(("Redirect to %s -- Wait %s seconds.\n" % (redirect_info[1], redirect_info[0])))
		time.sleep(float(redirect_info[0]))
		return main_do(redirect_info[1],True,threadName,oper,timeout)

def p_w_url(url_list,worte=True,position=None):
	global url_top
	if url_list:
		insert_console_end("\n")
		for url in url_list:
			insert_console_end(url+"\n")
		if worte:
			write_file(url_list,position)
		insert_console_end(("\nTotaly Had %s pages in %s site.\n" % (str(len(url_list)),url_top)))
		del url_list
	else:
		insert_console_end(("\n%s doesn't have any link.\n" % url_top))
		del url_list
	stop_Button['state'] = "disabled"
	cmd.see(END)

def Control_out(url_scan,timeout,oper,self_site=True):
	rb_check = rm_robots(url_scan)
	if not rb_check:
		insert_console_end("Error : Can not use robots filter in %s now...\n" % url_scan)
	insert_console_end("Ready to catch url in this site. Starting....\n")
	url = main_do(url_scan,self_site,"Main-Thread",oper,timeout)
	return url

class createNewThread(threading.Thread):
	global message_queue
	message_queue = queue.Queue(maxsize=-1)
	def __init__(self,threadName,task,self_site,oper,timeout):
		self.self_site = self_site
		self.timeout = timeout
		self.oper = oper
		self.threadName = threadName
		self.task = task
		threading.Thread.__init__(self,name = threadName)
	def run(self):
		self_site = self.self_site
		timeout = self.timeout
		oper = self.oper
		task = self.task
		threadName = self.threadName
		url_new_found = [main_do(task,self_site,threadName,oper,timeout),task]
		message_queue.put(url_new_found)

def threadPool(num,con,task,self_site,timeout,oper):
	th = createNewThread(("Thread-"+str(num)),task,self_site,oper,timeout)
	con.put(th)

def thread_run_spider(url,self_site,timeout,oper,threadNum,writen_file,position):
	global url_top
	global message_queue
	global clear
	has_found = []
	has_found.append(url)
	has_found.append(url_top)
	url = Control_out(url_top,timeout,oper,self_site)
	url_top = 'http://'+url_top.split('/')[2]+"/"
	waitting_data = False
	if not url:
		insert_console_end("This site doesn't have any link.\n")
		run_spider_button['state'] = "normal"
		return False
	con = queue.Queue(maxsize=threadNum)
	num = 1
	for url_task in url[0:threadNum]:
		threadPool(num,con,url_task,self_site,timeout,oper)
		url.remove(url_task)
		has_found.append(url_task)
		num += 1
	while not con.empty():
		if threading.activeCount() > threadNum*2+1:
			continue
		if clear:
			while threading.activeCount() > 3:
				insert_console_end("Waitting retrieve threading...\n")
				time.sleep(0.5)
			while not con.empty:
				con.get_nowait() 
			while not message_queue.empty():
				message_queue.get_nowait()
			while len(has_found) != 0:
				has_found = []
			clear = False
			stop_Button['state'] = "disabled"
			return False
		th = con.get()
		th.setDaemon(True)
		th.start()
		if waitting_data:
			th.join()
		if not message_queue.empty():
			waitting_data = False
			url_tm = message_queue.get_nowait()
			if url_tm[0] and (len(url_tm[0]) != 0):
				insert_console_end(("About %s links on %s page.\n" % (str(len(url_tm[0])),url_tm[1])))
				url.extend(url_tm[0])
			else:
				insert_console_end(("There no pages on %s\n" % url_tm[1]))
			url = list({}.fromkeys(url).keys())
			url = list(set(url)-set(has_found))
			url = list(set(url) - set(unable_list.keys()))
			if len(url) <= threadNum:
				waitting_data = True
			if len(url) == 0:
				break
		else:
			waitting_data = True
		if con.empty():
			num = 1
			for url_task in url[0:threadNum]:
				threadPool(num,con,url_task,self_site,timeout,oper)
				url.remove(url_task)
				has_found.append(url_task)
				num += 1
	while threading.activeCount() > 2:
		insert_console_end("Waitting retrieve threading...\n")
		time.sleep(1)
	while message_queue.qsize() != 0:
		data = message_queue.get_nowait()[0]
		if data:
			has_found.extend(data)
	has_found = list({}.fromkeys(has_found).keys())
	run_spider_button['state'] = "normal"
	p_w_url(has_found,writen_file,position)
	if ((len(unable_list) != 0) and writen_file):
		if write_error_links(unable_list,url_top):
			messagebox.showinfo("提示","发现您的站点有%s条死链，已存储为wrong-links.txt，请查看" % len(unable_list))
	del has_found,url,data

# Combobox生成
th_list_choice = [(str(i)+"线程") for i in range(1,9)]
threadNum_in = Combobox(root, state="readonly", values=th_list_choice, width="10",justify="center")
explorer_in = Combobox(root, state="readonly", values=["Chrome","Internet Explorer"],justify="center")
threadNum_in.grid(row=2, column=3, sticky=W)
explorer_in.grid(row=2, column=1, sticky=W)
explorer_in.set("Chrome")
threadNum_in.set("4线程")

# CheckButton生成
def save_file():
	if writen_file_in.get():
		writen_file_in.set(True)
		file_Entry.configure(state="normal")
		file_select.configure(state="normal")
		root.update()
	else:
		position_in.set("")
		file_select.configure(state="disabled")
		file_Entry.configure(state="disabled")
		root.update()
writen_file_in,self_site_in,original_in,use_proxy_in = BooleanVar(), BooleanVar(), BooleanVar(), BooleanVar()
save_file_checkbutton = Checkbutton(root, text="保存url到文件", variable=writen_file_in, onvalue=True, offvalue=False,command=save_file)
self_site_checkbutton = Checkbutton(root, text="只爬取本站点", variable=self_site_in, onvalue=True, offvalue=False)
use_proxy_checkbutton = Checkbutton(root, text="使用系统代理", variable=use_proxy_in, onvalue=True, offvalue=False)
original_checkbutton = Checkbutton(root, text="提交为原创文章", variable=original_in, onvalue=True, offvalue=False)
original_checkbutton.grid(row=1, column=2, sticky=W, padx=25)
use_proxy_checkbutton.grid(row=4, column=2, sticky=W, padx=25)
save_file_checkbutton.grid(row=0, column=2, sticky=W, padx=25)
self_site_checkbutton.grid(row=0, column=3, sticky=W)
original_in.set(True)
writen_file_in.set(True)
self_site_in.set(True)
threadNum_in.configure(state="readonly")
threadNum_in.set("4线程(推荐)")

# Label生成
url_top_Label = Label(root, text="您的域名：").grid(row=0,sticky=W,padx=14)
key_url_Label = Label(root, text="提交密码：").grid(row=1,sticky=W,padx=14)
th_num_Label = Label(root, text="最大线程数设置：").grid(row=2,column=2,padx=25,sticky=W)
UA_Label = Label(root, text="UA 设置：").grid(row=2,sticky=W,padx=14,pady=10)
timeout_Label = Label(root, text="超时设置：").grid(row=4,sticky=E,padx=14)
timeout_set = Label(root, text="s : 单位").grid(row=4,column=1,sticky=E,ipadx=48)
file_Label = Label(root, text="文件位置：").grid(row=3,sticky=E,padx=14,pady=10)
toolbox_Label = Label(root, text="控制工具：").grid(row=6,sticky=W,padx=14)

# Entry生成
url_top_in, key_url_in, timeout_in, position_in = StringVar(), StringVar(), StringVar(), StringVar()
url_top_Entry = Entry(root,textvariable=url_top_in,width="36",font=('Microsoft Yahei','9','bold'))
key_url_Entry = Entry(root,textvariable=key_url_in,width="22",font=('Microsoft Yahei','9','bold'),show="●")
time_out_Entry = Entry(root,textvariable=timeout_in,width="15",justify="center")
file_Entry = Entry(root, textvariable=position_in,width="36",font=('Microsoft Yahei','9','bold'),state="normal")
url_top_Entry.grid(row=0, column=1, pady=10)
key_url_Entry.grid(row=1, column=1, pady=10, sticky=W, ipadx=1)
time_out_Entry.grid(row=4, column=1, pady=10, sticky=W)
file_Entry.grid(row=3, column=1, pady=10)
timeout_in.set("4")

# Button生成
def show_timeout_info():
	timeout_info = """超时时间指的是在爬取URL时遇到响应缓慢的URL的最大等待时间，单位为秒，最大值为3600
最小值为0（指不等待，此时会无法爬取）默认值为4S，超过响应阀值后会提示timeout错误，进行下一个URL"""
	messagebox.showinfo('帮助-超时时间',timeout_info)
def show_th_info():
	warn_th = """多线程会明显加快爬虫爬取速度，尤其当被爬取网站延迟较高时。
在实际测试中，线程数过大时，往往会导致网站并发不够，导致很多连接爬取失败，请谨慎设置（软件支持最大线程数8，超过会出现问题）。
推荐您设置4个线程。"""
	messagebox.showinfo('帮助-多线程支持',warn_th)
warn_th_Button = Button(root, text="关于多线程",width=12, command=show_th_info)
warn_th_Button.grid(row=1, column=3, sticky=W)
def show_UA_info():
	UA_info = """UA就是User-Agent的简称，作为网站访问者的身份，
爬虫需要使用UA来给自己一个身份。
否则大部分情况会被网站禁止访问，这个蜘蛛使用了浏览器的UA，来确保爬取站点成功。
"""
	messagebox.showinfo('帮助-关于UA设置',UA_info)
def show_key_url_info():
	key_url_info = """这个提交密码是指您在百度站长平台上所获取到的推送数据接口调用地址，具体您需要：
登陆站长平台 ——> 我的网站 ——> 链接提交 ——> 接口调用地址 
中查看调用地址，您还可以在平台修改调用地址。"""
	messagebox.showinfo("关于密码",key_url_info)
def show_proxy_info():
	proxy_info = """系统代理是的是您当前系统设置的代理，与您的设置有关，
另外例如ss等某些软件也会改变您的系统代理设置，如果开启此选项，
蜘蛛的网络将会与您的系统设置相同。
注意不稳定或速度慢的代理服务器可能会严重拖慢蜘蛛的速度，如非必要，请勿开启。"""
	messagebox.showinfo("关于系统代理",proxy_info)
show_key_url_Button = Button(root,text="关于密码", command=show_key_url_info)
show_key_url_Button.grid(row=1 ,column=1, sticky=E)
show_UA_Button = Button(root,text="关于UA", command=show_UA_info)
show_proxy_Button = Button(root,text="关于系统代理",width=12, command=show_proxy_info)
show_proxy_Button.grid(row=4,column=3, sticky=W)
show_UA_Button.grid(row=2, column=1, sticky=E)
show_timeout_Button = Button(root,text="关于超时", command=show_timeout_info)
show_timeout_Button.grid(row=4,column=1,pady=10,sticky=E)
file_select = Button(root,text="选择URL存储目录",command=CallFileDialog)
file_select.grid(row=3,column=2,sticky=W,padx=25)
save_config_Button = Button(root,text="储存默认配置",width=12, command=save_config)
save_config_Button.grid(row=3,column=3,sticky=W)
class make_myself:
	def show(self):
		top = Toplevel(root)
		self.top = top
		top.title("使用帮助 && 关于作者")
		top.geometry("460x530")
		top.resizable(False, False)
		top.iconbitmap("icon.ico")
		Label(top,text="使用帮助：").grid(sticky = NW,padx=15,pady=10)
		Label(top,text="1.首日使用完之后是暂时无法提交更新的，在次日爬取链接之后即可比对提交。").grid(sticky = W,padx=30,pady=5)
		Label(top,text="2.每当记录文件大于8天时，会自动清理以前的记录文件。").grid(sticky = W,padx=30,pady=5)
		Label(top,text="3.您可以使用完全的URL地址作为密钥，也可以单独使用密钥。").grid(sticky = W,padx=30,pady=5)
		Label(top,text="4.请不要设置过大的线程数，会导致蜘蛛被屏蔽/网站压力过大。").grid(sticky = W,padx=30,pady=5)
		Label(top,text="5.请根据您的需要及实际情况选择是否提交原创文章。").grid(sticky = W,padx=30, pady=5)
		Label(top,text="6.可能生成的文件以及说明: ").grid(sticky = W,padx=30,pady=5)
		Label(top,text="\truntime.log-控制台日志文件:不用可以删除 ;").grid(sticky = W,padx=30,pady=2)
		Label(top,text="\tconfig.conf-配置文件:删除之后您无法使用保存的配置 ; ").grid(sticky = W,padx=30,pady=2)
		Label(top,text="\t存储目录下的*.bak/.dir/.dat-记录文件:请不要删除。").grid(sticky = W,padx=30,pady=2)
		Label(top,text="关于作者：").grid(sticky = NW,padx=15,pady=15)
		Label(top,text="1.作者是一只高三狗，尚无女朋友，联系我，可以到站点留言。").grid(sticky = W,padx=30,pady=0)
		Label(top,text="2.任何疑问/建议，请发邮件至guiqiqi187@gmail.com，我会在3天之内回复。").grid(sticky = W,padx=30,pady=10)
		Label(top,text="\t作者：桂QQ（guiqiqi187@gmail.com） ； 版本：%s " % version).grid(sticky = W,padx=10,pady=10)
		Button(top,text="看看作者 && 留个言",command=self.open_site,width=25).grid(row=20,column=0,sticky = W,pady=10,padx=130)
	def open_site(self):
		webbrowser.open("http://www.nfishs.com/archives/988")
make_myself = make_myself()
run_spider_button = Button(root,text="运行蜘蛛爬取数据更新",command=start_GUI_spider)
run_spider_button.grid(row=8,columnspan=3,rowspan=2,ipady=15,sticky=W,padx=110,pady=20)
run_baidu_button = Button(root,text="提交数据到百度站长平台",command=start_update)
run_baidu_button.grid(row=8,columnspan=3,column=2,rowspan=2,ipady=15,sticky=W,padx=20)
Separator(root).grid(row=5,sticky=EW,columnspan=8)
query_Button = Button(root,text="查询剩余推送量",width="15",command=query_remain)
query_Button.grid(row=6,sticky=W,padx=0,column=1,pady=15)
stop_Button = Button(root,text="停止当前爬取",width="15",command=stop_spider)
stop_Button.grid(row=6,sticky=W,padx=143,column=1,columnspan=2)
do_check = lambda : (threading.Thread(target=check_software_update).start())
check_software_update_Button = Button(root,text="检查软件更新",width="14",command=do_check)
check_software_update_Button.grid(row=6,sticky=W,padx=23,column=2,columnspan=2)
stop_Button['state'] = "disabled"
open_panel = lambda : ConfigControlPanel()
control_panel_Button = Button(root,text="管理配置文件",width="14",command=open_panel)
control_panel_Button.grid(row=6,sticky=E,padx=13,column=2,columnspan=2)
Separator(root).grid(row=7,sticky=EW,columnspan=8)
about_Button = Button(root,text="使用帮助",width="12",command=make_myself.show)
about_Button.grid(row=11,column=1,sticky=W,padx=170,columnspan=3)
clear_Button = Button(root,text="清除控制台",command=lambda:clear_cmd(True))
clear_Button.grid(row=11,sticky=W,column=1,padx=30,pady=10)
save_log_Button = Button(root,text="存储为.log日志",command=save_log)
save_log_Button.grid(row=11,sticky=E,column=2,padx=30)

# 右键菜单栏支持
class section:
	def __init__(self,target,Entry):
		self.target = target
		self.Entry = Entry
	def onPaste(self):
		target = self.target
		try:
			self.text = root.clipboard_get()
		except TclError:
			pass
		try:
			target.set(str(self.text))
		except:
			pass
	def onCopy(self):
		Entry = self.Entry
		self.text = Entry.get()
		root.clipboard_append(self.text)
	def onCut(self):
		Entry = self.Entry
		self.onCopy()
		try:
			Entry.delete('sel.first','sel.last')
		except TclError:
			pass
section_key_url = section(key_url_in,key_url_Entry)
menu_key_url = Menu(root,tearoff=0)
def add_command(menu_target):
	menu_target.add_command(label="复制",command=section_key_url.onCopy)
	menu_target.add_separator()
	menu_target.add_command(label="粘贴",command=section_key_url.onPaste)
	menu_target.add_separator()
	menu_target.add_command(label="剪切",command=section_key_url.onCut)
add_command(menu_key_url)

# 添加控制输出
cmd = Text(root,height="18",width="83",insertborderwidth=2)
cmd.grid(row=10,columnspan=6,column=0,padx=17,sticky=W)
cmd.focus_set()
scrollY = Scrollbar(root,orient=VERTICAL,command=cmd.yview)
scrollY.grid(row=10,column=3,sticky=NS,columnspan=8,padx=87)
cmd['yscrollcommand'] = scrollY.set
# scrollX = Scrollbar(root,orient=HORIZONTAL,command=cmd.xview)
# cmd['xscrollcommand'] = scrollX.set
# scrollX.grid(row=8,sticky="WE",columnspan=4)

def popupmenu_url_top(event):
	menu_url_top.post(event.x_root,event.y_root)
def popupmenu_key_url(event):
	menu_key_url.post(event.x_root,event.y_root)
def popupmenu_file(event):
	menu_file.post(event.x_root,event.y_root)
def show_pass(event):
	key_url_Entry.configure(show="")
def hide_pass(event):
	key_url_Entry.configure(show="●")

key_url_Entry.bind("<Button-3>",popupmenu_key_url)
key_url_Entry.bind("<Enter>",show_pass)
key_url_Entry.bind("<Leave>",hide_pass)

root.title("Baidu站长平台提交工具")
root.resizable(False, False)
root.geometry("630x660+320+15")
root.iconbitmap('icon.ico')
use_config(load_config("default"))

if __name__ == "__main__":
	root.mainloop()
