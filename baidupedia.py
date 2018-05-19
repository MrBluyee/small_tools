# -*- coding: UTF-8 -*-

__author__ = 'Mr.Bluyee'

import urllib3
import json
import certifi
import io
import sys
import re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
#改变标准输出的默认编码
class BaiduPedia(object):
	def __init__(self):
		self.html_data = ''
		self.title = ''
		self.other_pedias_list = []

	def make_https_request(self,url,func,field = {}):
		https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
		request_head = {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'}
		r = https.request(func, url,fields = field,headers = request_head)
		if r.status == 200:
			self.html_data = r.data.decode('utf-8')
		
	def baidu_pedia_request(self,word):
		url = 'https://baike.baidu.com/search/word'
		func = 'GET'
		field = {'word':word}
		self.make_https_request(url,func,field)

	def save_file(self,web_data,filename):
		with open(filename,'w') as f:
			f.write(web_data)
		
	def baidupedia_get_title(self,s):
		pattern = re.compile(r'<title>.*?</title>', re.S)
		self.title = pattern.search(s).group()[7:-13]
	
	def baidupedia_get_other_pedias_dict(self,s):
		pattern = re.compile(r'<li class="item">▪<a title=.*?</a></li>', re.S)
		other_pedias = pattern.findall(s)
		if len(other_pedias) > 0:
			print('')
			print('该词是一个多义词，请在下列义项上选择浏览:')
			print('1' + self.title)
			num_index = 2
			for item in other_pedias:
				index1 = item.find('href')
				index2 = item.find('>',index1)
				other_pedias_href = 'https://baike.baidu.com' + item[index1 + 6:index2 - 1]
				other_pedias_title = item[index2 + 1:-9]
				print(str(num_index) + other_pedias_title)
				num_index += 1
				self.other_pedias_list.append(other_pedias_href)
			print('')
	
	def baidupedia_get_summary(self,s):
		print(self.title)
		print('')
		pattern = re.compile(r'<div class="promotion-declaration">.*?</dl></div>', re.S)
		head_content = pattern.search(s).group()
		head_content = re.sub(r'<[\u0008-\u007F]*?>','',head_content)
		head_content = re.sub(r'\n\n*','\n',head_content)
		head_content = re.sub(r'&nbsp;','',head_content)
		print(head_content)
		
	def baidupedia_get_content(self,s):
		pattern = re.compile(r'<a name="\d.*?" class="lemma-anchor para-title".*?<div class="anchor-list">', re.S)
		content = pattern.findall(s)
		for item in content:
			item_pattern1 = re.compile(r'<span class="title-prefix">.*?</h.*?\d', re.S)
			item_content1 = item_pattern1.search(item).group()
			item_catalogue =  re.sub(r'<.*?n>','',item_content1)
			if item_catalogue[-1] == '2':
				print('---' + item_catalogue[:-4])
			elif item_catalogue[-1] == '3':
				print('------' + item_catalogue[:-4])
			item_pattern2 = re.compile(r'<div class="para" label-module="para">.*?</div>', re.S)
			item_content2 = item_pattern2.findall(item)
			for item_child in item_content2:
				item_child_content1 = re.sub(r'<[\u0008-\u007F\u4e00-\u9fa5]*?>\r*\n*', '', item_child)
				item_child_content1 = re.sub(r'&.*?;','',item_child_content1)
				if item_catalogue[-1] == '2':
					print('   ' + item_child_content1)
				elif item_catalogue[-1] == '3':
					print('      ' + item_child_content1)
			print('')
		
	def baidupedia_match(self,s):
		self.baidupedia_get_summary(s)
		self.baidupedia_get_content(s)
		
	def baidupedia(self,word):
		self.baidu_pedia_request(word)
		self.baidupedia_get_title(self.html_data)
		self.baidupedia_get_other_pedias_dict(self.html_data)
		list_len = len(self.other_pedias_list)
		if list_len > 0:
			num = int(input('请输入你要查的意思：'))
			print('')
			if num == 1:
				self.baidupedia_match(self.html_data)
			else:
				self.make_https_request(self.other_pedias_list[num - 2],'GET')
				self.baidupedia_get_title(self.html_data)
				self.baidupedia_match(self.html_data)
		else:
			self.baidupedia_match(self.html_data)
		
def main():
	word = input('请输入你要查的词语：')
	baidu_pedia = BaiduPedia()
	baidu_pedia.baidupedia(word)
	
if __name__ == '__main__':
	main()
