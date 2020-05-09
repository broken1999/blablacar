#
	
# define class Blabla	
class Blabla:
	def startdate(self,startdate):
		self.startdate=startdate
	def starttime(self,starttime):
		self.starttime=starttime
	def duration(self,duration):
		self.duration=duration
	def departure(self,departure):
		self.departure=departure
	def destination(self,destination):
		self.destination=destination
	def departurenation(self,departure):
		self.departure=departure
	def destinationnation(self,destination):
		self.destination=destination
	def distance(self,distance):
		self.distance=distance
	def price(self,price):
		self.price=price
	def pricecolor(self,pricecolor):
		self.pricecolor=pricecolor
	def kmpereuro(self,kmpereuro):
		self.kmpereuro=kmpereuro
	def availability(self,availability):
		self.availability=availability


# import 		
import re
import urllib2
import os
from bs4 import BeautifulSoup

# initialize result list
resultslist=[]
f=open('result.dat','a+')
f.write("startdate\t starttime\t price\t pricecolor\t availability\t departure\t destination\t distance\t kmpereuro\t duration\t\n")
print("startdate\t starttime\t price\t pricecolor\t availability\t departure\t destination\t distance\t kmpereuro\t duration\t")

# get the total pages
limit=100
soup = BeautifulSoup(urllib2.urlopen('https://www.blablacar.de/mitfahren/zuerich/#?fn=Z%C3%BCrich,%20Schweiz&fc=47.3768866%7C8.541694&fcc=CH&tn=&sort=trip_price_euro&order=asc&limit='+str(limit)+'&page=1'))
totalnumofresults=int(str(soup('span',{'class':'trip-search-title-count'})[0].prettify()).splitlines()[1])
totalnumofpages=totalnumofresults/limit+1
os.system('echo \'\' > soup.html')

# fetch the results
for page in range(1,totalnumofpages):
	
	# load data from website
	os.system('cp ./phantomjs-2.1.1-linux-x86_64/bin/savepage .')
	os.system('sed -i \'s/page=/page='+str(page)+'/g\' ./savepage')
	os.system('./phantomjs-2.1.1-linux-x86_64/bin/phantomjs ./savepage > soup.html')

	# extract from downloaded web page
	soup = BeautifulSoup(open("./soup.html").read())
	
	# empty result object for new hit
	result=Blabla()
	
	# append result to list, ten results per page
	for i in range(0,limit):
	
		# startDate
		temp= soup('h3',{'itemprop':'startDate'})[i]['content']
		result.startdate=temp
				
		# starttime
		temp= str(soup('h3',{'itemprop':'startDate'})[i])
		rg = re.compile('(\\d)(\\d)(:)(\\d)(\\d)',re.IGNORECASE|re.DOTALL)
		m = rg.search(temp)
		if m:
			d1=m.group(1)
			d2=m.group(2)
			c1=m.group(3)
			d3=m.group(4)
			d4=m.group(5)
		result.starttime=d1+d2+c1+d3+d4
		
		# price
		temp=soup('strong',{'class':''})
		j=0
		k=0
		for row in temp:
			if '€' in str(row):
				k=k+1
			if k>i:
				break
			j=j+1	
		result.price=[int(s) for s in temp[j]('span')[0].string.split() if s.isdigit()][0]
		
		# pricecolor
		result.pricecolor=soup('div',{'class',"price"})[i].get('class')[1]
		
		# availability
		result.availability=soup('div',{'class',"availability"})[i]('strong')[0].string
		
		# departure
		result.departure=soup('span',{'class':'from trip-roads-stop'})[i].string
		dep=soup('dd',{'oldtitle':'Abfahrt'})[i].string
		
		# destination
		result.destination=soup('span',{'class':'trip-roads-stop'})[i*2+1].string
		des=soup('dd',{'oldtitle':'Ankunft'})[i].string
		
		# prepare distance matrix
		departure=dep
		if dep.find('Abfahrt:')>-1:
			depbegin=dep.split().index('Abfahrt:')
			depend=dep.split().index('(Bitte')
			departure="".join(dep.split()[depbegin+1:depend])
		destination=des
		if des.find('Ankunft:')>-1:
			desbegin=des.split().index('Ankunft:')
			desend=des.split().index('(Bitte')
			destination="".join(des.split()[desbegin+1:desend])
		try :
			soupfordistance = BeautifulSoup(urllib2.urlopen('https://maps.googleapis.com/maps/api/distancematrix/xml?origins='+"".join(departure.encode('utf-8').split())+'&destinations='+"".join(destination.encode('utf-8').split())+'&key=####&mode=driving'))
			# check availability of distance matrix
			status=soupfordistance('status')[1].string
		
			if status=='NOT_FOUND' or status=='ZERO_RESULTS' :
				result.distance=1
				result.duration=999
			else:			
				# distance
				result.distance= int(soupfordistance('distance')[0]('value')[0].string)
				# duration
				result.duration= int(soupfordistance('duration')[0]('value')[0].string)/3600.00
		except :
			result.distance=1
			result.duration=999
		
		# km/euro
		result.kmpereuro= result.distance/result.price/1000.00
		
		print "%s \t %s \t %d \t %s \t %s \t %s \t %s \t %d \t %d \t %d"  % (result.startdate,result.starttime,result.price,result.pricecolor,result.availability,result.departure,result.destination,result.distance,result.kmpereuro,result.duration)
		f.write("%s \t %s \t %d \t %s \t %s \t %s \t %s \t %d \t %d \t %d\n"  % (result.startdate.encode('utf-8'),result.starttime.encode('utf-8'),result.price,result.pricecolor.encode('utf-8'),result.availability.encode('utf-8'),result.departure.encode('utf-8'),result.destination.encode('utf-8'),result.distance,result.kmpereuro,result.duration))
		
		# result append to list
		resultslist.append(result)
		

f.close()
# delete intermediate file
os.system('rm soup.html')

# reorganise	

