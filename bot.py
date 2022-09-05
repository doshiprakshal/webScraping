from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen as uReq,Request
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pymongo import MongoClient
# connecting to db
try:
    conn = MongoClient()
    print("Connected successfully!!!")
except:  
    print("Could not connect to MongoDB")
 

db = conn.database
collection = db.crimsonInsights

# path
binary = FirefoxBinary('C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')
capabilities = webdriver.DesiredCapabilities.FIREFOX
capabilities["marionette"] = True


url = 'https://www.perkinscoie.com/en/professionals/index.html?start=0'

# create a new Firefox session
driver = webdriver.Firefox(firefox_binary=binary, capabilities=capabilities)
driver.implicitly_wait(30)
driver.get(url)

# wait for 10 secs to get the website completely loaded
time.sleep(10)
soup=BeautifulSoup(driver.page_source, "html.parser")

#get all the lawyers link
x = soup.findAll('div', class_='results-block__column results-block__name')

#base url
i = 'https://www.perkinscoie.com'

#iterate through each lawyer and get the link
for link in x:
	y = link.find('a', class_='results-block__name-link type-52-th', href = True)

	#request the url of lawyer eg: 'https://www.perkinscoie.com/en/professionals/thomas-n-abbott.html'
	req = Request(i+y['href'], headers={'User-Agent': 'Mozilla/5.0'})
	html = uReq(req).read()
	uReq(req).close()
	bsObj = BeautifulSoup(html, "html.parser")

	#getting the required details
	areaOfFocus = list()
	full_name = bsObj.find('span', class_='bio-title-text')
	first_name = full_name.text.split(" ")
	position = bsObj.find('span', class_='bio-position type-25')
	office = bsObj.find('a', class_='type-27')
	phone = bsObj.findAll('span', class_='phone-number')
	ph1 = phone[0].text
	vcard = bsObj.findAll('a', class_='type-29', href = True)
	vcardLink = i+vcard[0]['href']
	email = vcard[1]['href'].split('mailto:')
	overview = bsObj.find('div',class_='side-item-wrapper')
	aof = bsObj.find('div',class_='side-item-list')
	temp = aof.findAll('li')
	for t in temp:
		areaOfFocus.append(t.text)
	
	#checking if isPatentLawyer is true/false
	isPatent = False
	if "patent" in overview.text or "intellectual property" in overview.text:
		isPatent = True
	if isPatent == False:
		for aoff in areaOfFocus:
			if "patent" in aoff or "intellectual property" in aoff:
				isPatent = True
				break
	
	#object to insert into database
	data = {
			"lawyersFullName": full_name.text,
			"lawyerFirstName": first_name[4],
			"lawyerPosition": position.text,
			"lawyerOffice": office.text,
			"lawyerPhone": ph1,
			"lawyerEmail": email[1],
			"lawyerVCardLink": vcardLink,
			"lawyerOverview": overview.text,
			"lawyerAreaOfFocus": areaOfFocus,
			"isPatentLawyer": isPatent,
			"lawyerUrl": i+y['href']
	}
	rec = collection.insert_one(data)
	print("inserted data: ",rec)

#printing the data inserted into database
getData = collection.find()
for record in getData:
	print(record)
	