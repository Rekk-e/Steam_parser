from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ui import Ui_MainWindow
from bs4 import BeautifulSoup as bs
import requests
import csv
from random import choice
from selenium import webdriver
import sys
from PyQt5.QtCore import QThread

global cost


def get_link(url, headers):
		catalog = []
		proxy = get_proxy()
		print(proxy)
		resp = requests.get(url, headers=headers, proxies=proxy).text
		total_cout = resp.split(',"tip":"Set')[0].split('"total_count":')[-1]
		soup = requests.get(url.replace('count=all', 'count={}'.format(total_cout)), headers=headers, proxies=proxy).text
		obrz = soup.split('\/listings\/')
		for i in obrz:
			obrz2 = i.split("resultlink_")
			for z in obrz2:
				obrz3 = z.split('\\" id=\\')
				if len(obrz3) == 2 and (obrz3[0].split('market_recent')[-1] != '_listing_row market_listing_searchresult'):
					catalog.append('https://steamcommunity.com/market/listings/' + obrz3[0])

		price = soup.split('data-currency=')
		pricestick = []
		for i in price:
			price2 = i.split('<\\/span>\\r\\n\\t\\t\\t\\t\\t<span class=\\')
			if '$' in price2[0].split('>')[-1]:
				withstick = price2[0].split('>')[-1]
				pricestick.append(withstick)

		return catalog, pricestick

def get_proxy():
		proxyurl = 'https://free-proxy-list.net/'
		r = requests.get(proxyurl, verify=False)
		soup = bs(r.text, 'lxml')
		table = soup.find('table',{'id':'proxylisttable'}).find_all('tr')[1:21]
		proxies = []
		for i in table:
			tds = i.find_all('td')
			if tds[6].text == 'yes':
				ip = tds[0].text.strip()
				port = tds[1].text.strip()
				schema = tds[6].text
				proxy = {'schema':schema,
						'ip': ip + ':' + port}
				proxies.append(proxy)

		return(choice(proxies))

def get_html(url, headers):
		p = get_proxy()
		proxy = { p['schema']: p['ip'] }
		response = requests.get(url, headers=headers, proxies=proxy)
		soup = bs(response.text, 'lxml')

		return soup

def get_weapon(url, headers):
		driver.get(url)
		name = driver.find_element_by_id('largeiteminfo_item_name').text.split(' ')[-1]
		qual = driver.find_element_by_id('largeiteminfo_item_descriptors').find_elements_by_class_name('descriptor')[0].text.split(': ')[-1]
		simpleprice = ''
		while not('$' in simpleprice):
			coordinates = driver.find_element_by_id('market_commodity_buyrequests').location_once_scrolled_into_view # returns dict of X, Y coordinates
			driver.execute_script('window.scrollTo({}, {});'.format(coordinates['x'], coordinates['y']))
			simpleprice = driver.find_element_by_id('market_commodity_buyrequests').text.split(': ')[-1]

		return name, qual, simpleprice

class Thread(QThread):
	def __init__(self, MyWind, parent=None):
		super().__init__()
		self.mainwindow = MyWind

	def run(self):
		headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
		catalog, withstick = get_link(url, headers)
		cost = -1
		lcd = 0
		for i in catalog:
			cost += 1
			lcd += 1
			print(cost)
			name, qual, simpleprice = get_weapon(i, headers)
			rowPosition = self.mainwindow.ui.tableWidget.rowCount()
			self.mainwindow.ui.tableWidget.insertRow(rowPosition)
			self.mainwindow.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(i))
			self.mainwindow.ui.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(name))
			self.mainwindow.ui.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(withstick[cost].split(' ')[0]))
			self.mainwindow.ui.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(simpleprice))
			self.mainwindow.ui.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(qual))
			self.mainwindow.ui.lcdNumber.display(lcd)



class MyWin(QtWidgets.QMainWindow):

	def __init__(self, parent=None):
		QtWidgets.QWidget.__init__(self, parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.comboBox.activated.connect(self.chose_url)
		self.ui.comboBox_2.activated.connect(self.chose_stickcurrent)
		self.ui.comboBox_3.activated.connect(self.chose_save)
		self.ui.comboBox_4.activated.connect(self.chose_quality)
		self.ui.lineEdit.textChanged.connect(self.chose_price)
		self.ui.lineEdit_2.textChanged.connect(self.chose_price)
		self.ui.lineEdit_3.textChanged.connect(self.chose_current)
		self.ui.pushButton.clicked.connect(self.chose_url)
		self.ui.pushButton.clicked.connect(self.launch)

		self.Thread_instance = Thread(MyWind=self)


	def chose_current(self):
		global saves
		saves = int(self.ui.lineEdit_3.toPlainText())

	def chose_save(self):
		global save
		if self.ui.comboBox_3.currentText() == 'txt':
			save = 0
		if self.ui.comboBox_3.currentText() == 'excel':
			save = 1
		
	def chose_price(self):
		global minprice, maxprice
		minprice = self.ui.lineEdit.toPlainText()
		maxprice = self.ui.lineEdit_2.toPlainText() 


	def chose_quality(self):
		global quality

		if self.ui.comboBox_3.currentText() == 'Любое качество':
			quality = 'all'

	def chose_stickcurrent(self):
		global current

		if self.ui.comboBox_2.currentText() == '2 одинаковых стикера':
			current = 2
		if self.ui.comboBox_2.currentText() == '3 одинаковых стикера':
			current = 3
		if self.ui.comboBox_2.currentText() == '4 одинаковых стикера':
			current = 4
		else:
			current = 'all'

	def chose_url(self):
		global url

		if self.ui.comboBox.currentText() == 'Desert Eagle':
			url = 'https://steamcommunity.com/market/search/render/?query=STICKER&start=0&count=all&search_descriptions=1&sort_column=default&sort_dir=desc&appid=730&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=tag_weapon_deagle'
		if self.ui.comboBox.currentText() == 'USP-S':
			url = 'https://steamcommunity.com/market/search/render/?query=STICKER&start=0&count=all&search_descriptions=1&sort_column=default&sort_dir=desc&appid=730&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=tag_weapon_usp_silencer'
		if self.ui.comboBox.currentText() == 'AWP':
			url = 'https://steamcommunity.com/market/search/render/?query=STICKER&start=0&count=all&search_descriptions=1&sort_column=default&sort_dir=desc&appid=730&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=tag_weapon_usp_silencer'

	def launch(self):
		self.Thread_instance.start()


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	myapp = MyWin()
	myapp.show()
	driver = webdriver.PhantomJS()
	sys.exit(app.exec_())