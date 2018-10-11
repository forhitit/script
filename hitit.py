from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup
import re
from time import sleep

from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify

app = Flask(__name__)
api = Api(app)


# http://127.0.0.1:5000/hitit/QYRZC5

class HitIt(Resource):
    
    def get(self,input_pnr):

		# options = Options()
		# options.add_argument("--headless")

		# driver = webdriver.Firefox(firefox_options=options)
		
		driver = webdriver.Firefox()
		
		driver.get("https://agency-pia.crane.aero/Login.jsp")
		sleep(3)

		username = driver.find_element_by_name("USERNAME")
		password = driver.find_element_by_name("PASSWORD")

		username.send_keys("A072XW31")
		password.send_keys("Test1234")

		form = driver.find_element_by_name('form1')
		form.submit()

		sleep(2)

		driver.get("https://agency-pia.crane.aero/PNRManagement.jsp")
		sleep(3)
		
		pnr = driver.find_element_by_name("TBPNRNO")

		# pnr.send_keys("Q8CBUD")
		# pnr.send_keys("QYRZC5")
		pnr.send_keys(input_pnr)
		sleep(2)
		pnrBtn = driver.find_elements_by_class_name('stdbtnnrmWithFrame')[0].click()
		sleep(5)
		

		html = driver.page_source
		soup = BeautifulSoup(html,'html.parser')

		########################################################################################################################

		# For table #11  contact Person information

		ContactPerson = soup.findAll('table')[11].findAll('tr')[1].find('td').find('table').find('tbody').find('tr').findAll('td')[3].get_text().strip()
		Status = soup.findAll('table')[11].findAll('tr')[1].find('td').find('table').find('tbody').findAll('tr')[2].findAll('td')[1].get_text().strip()
		TelePhone = soup.findAll('table')[11].findAll('tr')[1].find('td').find('table').find('tbody').findAll('tr')[2].findAll('td')[3].get_text().strip()
		Email = soup.findAll('table')[11].findAll('tr')[1].find('td').find('table').find('tbody').findAll('tr')[3].findAll('td')[3].get_text().strip()
		CreatedDate = soup.findAll('table')[11].findAll('tr')[1].find('td').find('table').find('tbody').findAll('tr')[5].findAll('td')[1].get_text().strip()


		##################################################################################################################
		# For PNR Pax Table

		PaxDetailsTable = soup.find("div", {"id": "main"}).find('tbody').findAll('tr')

		PaxList = {}

		for table_row in PaxDetailsTable:
			cells = table_row.findAll('td')
			# print(cells)
			if len(cells) > 2:
				data = {}
				data.update({'SurName': cells[1].text.strip()})
				data.update({'Name': cells[2].text.strip()})
				data.update({'Gender': cells[3].text.strip()})
				data.update({'DOB': cells[4].text.strip()})
				data.update({'PaxType': cells[5].text.strip()})
			
				PaxList.setdefault('UserData', []).append({'Data':data})
		PaxList.update({'ContactPerson': ContactPerson})
		PaxList.update({'Status': Status})
		PaxList.update({'TelePhone': TelePhone})
		PaxList.update({'Email': Email})
		PaxList.update({'CreatedDate': CreatedDate})
		# ########################################################################################################################

		if Status != "Canceled PNR":
			sleep(5)
			html = driver.page_source
			soup = BeautifulSoup(html,'html.parser')


			TotalFarediv = soup.find("div", {"class": "total__fare"})
			TotalFare = TotalFarediv.find("div",{"class":"fare"}).get_text().strip()
		
		driver.quit()
 		return jsonify(PaxList)

 		

api.add_resource(HitIt, '/hitit/<string:input_pnr>')


if __name__ == '__main__':
     app.run()