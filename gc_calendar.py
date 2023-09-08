# coding=utf-8
import re,codecs,datetime,os, sys
import locale
from datetime import date, timedelta
import calendar
import json

locale.setlocale(locale.LC_TIME, "uk_UA")

easter_date_str = sys.argv[1] # YYYY-MM-DD
easter_date = datetime.datetime(*[int(item) for item in easter_date_str.split('-')]).date()

year = easter_date.year

fixed_dates = {} # is loaded from the file

month_sizes = [31, 29 if calendar.isleap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

entry_types = {"місяця":-1,"січня":1,"лютого":2,"березня":3,"квітня":4,"травня":5,"червня":6,"липня":7,"серпня":8,"вересня":9,"жовтня":10,"листопада":11,"грудня":12}

week_days = {"понеділок":0,"вівторок":1,"середа":2,"четвер":3,"пт":4,"субота":5,"неділя":6}

week_days_short = {0 : "П", 1: "В",2:"С" ,3:"Ч" ,4:"П", 5:"С", 6:"Н"}
month_names = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"];

tokens_to_months = {'{{january}}': 0, '{{february}}':1,'{{march}}':2,'{{april}}':3,'{{may}}':4,'{{june}}':5,'{{july}}':6,'{{august}}':7,'{{september}}':8,'{{october}}':9,'{{november}}':10,'{{december}}':11}
longFastingsToken = "{{long-fastings}}"
oneDayFastingsToken = "{{one-day-fastings}}"
fastingFreeTimesToken = "{{fasting-free-times}}"
forbiddenTimesToken = "{{forbidden-times}}"

days = []
entry_by_date = {}
date_by_label = {}
conditions = []

oneDayFastings = []
longFastings = []
forbiddenTimes = []
fastFreeTimes = []

nestedEntryRegex = re.compile("\{(.*)\}")
fixedDateRegex = re.compile("^([0-9]{1,2}) (січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)$", re.U)
#labelRegex = re.compile("^([абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ]+).*:$", re.U)
labelRegex = re.compile("^(.+):$")
conditionRegex = re.compile("(.+),(.+):(.+)")
def readLine(_file):
	while True:
		line = _file.readline()
		if not line:
			break
		if (line.startswith("#") or 3 > len(line)): # comment or empty string
			continue
		else:
			line = line.strip()
			break

	return line

def readLineEvenIfEmpty(_file):
	while True:
		line = _file.readline()
		if not line:
			break
		if line.startswith("#"): # comment or empty string
			continue
		else:
			line = line.strip()
			break

	return line

def readFile(fileName, entryType):
	file = open(fileName,"r")
	while 1:
		line1 = readLine(file)

		if not line1:
			break

		labelMatcher = labelRegex.match(line1);
		label = None
	
		if (labelMatcher):
			label = labelMatcher.group(1)
			entryValue = readLine(file)
		else:
			entryValue = line1
	
		line2 = readLine(file)
		
		entry = buildEntryFromLine(line2)
		entry.value = entryValue
		entry.value_type = entryType
		if label:
			entry.label = label
		for d in entry.dates:
			if d.year == year:
				entry_by_date[d].append(entry)
			if label:
				date_by_label[label] = d

def readSaints():
	print("Read saints")
	readFile("new-style/saints.txt", "saint")

def readCelebr():
	print("Read celebr")
	readFile("new-style/celebr.txt", "sundays")
	
def readAdditional():
	print("Read additional")
	readFile("new-style/add.txt", "additional")

def readConditions():
	file = open("new-style/conditions","r")
	while 1:
		line1 = readLine(file)
		if not line1:
			break
		matcher = conditionRegex.match(line1)
		if ( None == matcher):
			print("Failed to parse condition line: " + line1)
			continue
		condition = Condition()
		condition.entry1 = matcher.group(1).strip()
		condition.entry2 = matcher.group(2).strip()
		condition.entryToLeave = matcher.group(3).strip()
		conditions.append(condition)

def readFastings():
	file = open("new-style/fastings.txt","r")
	while 1:
		line1 = readLine(file)
		if not line1:
			break
		dateRange = DateRange()
		dateRange.title = line1
		line2 = readLineEvenIfEmpty(file)
		if not line2:
			longFastings.append(dateRange)
		else:
			startDateEntry = buildEntryFromLine(line2)
			dateRange.startDate = startDateEntry.dates[0]
			line3 = readLineEvenIfEmpty(file)
			if not line3:
				oneDayFastings.append(dateRange)
			else:
				endDateEntry = buildEntryFromLine(line3)
				dateRange.endDate = endDateEntry.dates[0]
				longFastings.append(dateRange)
	file.close()

def readForbiddenTimes():
	file = open("new-style/forbidden-times.txt","r")
	while 1:
		line1 = readLine(file)
		if not line1:
			break
		dateRange = DateRange()
		dateRange.title = line1
		forbiddenTimes.append(dateRange)
		
		line2 = readLineEvenIfEmpty(file)
		if line2:
			startDateEntry = buildEntryFromLine(line2)
			dateRange.startDate = startDateEntry.dates[0]
			line3 = readLineEvenIfEmpty(file)
			if line3:
				endDateEntry = buildEntryFromLine(line3)
				dateRange.endDate = endDateEntry.dates[0]
	file.close()

def readFastFreeTimes():
	file = open("new-style/fast-free.txt","r")
	while 1:
		line1 = readLine(file)
		line2 = readLine(file)

		if not line1:
			break
		dateRange = DateRange()
		fastFreeTimes.append(dateRange)

		dateRange.startDate = buildEntryFromLine(line1).dates[0]
		dateRange.endDate = buildEntryFromLine(line2).dates[0]
	file.close()

def buildEntryFromLine(line):
	entry = Entry()
	entry.raw_value = line
	entry_tokens = line.split(" ")
	fixedDateMatcher = fixedDateRegex.match(line)
	if ( None != fixedDateMatcher):
		d = date(year, int(entry_types[fixedDateMatcher.group(2)]), int(fixedDateMatcher.group(1)))
		entry.dates.append(d)
	else:
		distance = entry_tokens[0]
		weekday = entry_tokens[1]

		if ("перед" == entry_tokens[2]):
			distance = "-" + distance
			startpoint = ' '.join(entry_tokens[3:])
		elif ("після" == entry_tokens[2]):
			distance = "+" + distance
			startpoint = ' '.join(entry_tokens[3:])
		else:
			assert entry_tokens[2] in entry_types
			startpoint = entry_tokens[2]
		nestedEntryMatcher = nestedEntryRegex.match(startpoint)
		if None != nestedEntryMatcher:
			nestedEntryString = nestedEntryMatcher.group(1)
			startpointEntry = buildEntryFromLine(nestedEntryString)
			for startPointDate in startpointEntry.dates:
				d = calculateDateFromFixedDate(startPointDate, weekday, distance)
				entry.dates.append(d)
		elif startpoint in fixed_dates:
			d = calculateDateFromFixedDate(fixed_dates[startpoint], weekday, distance)
			entry.dates.append(d)
		elif entry_types[startpoint] == -1:
			months = range(1,13)
			for month in months:
				d = calculateDateByEntry(month, weekday, distance)
				entry.dates.append(d)
		else:
			d = calculateDateByEntry(entry_types[startpoint], weekday, distance)
			entry.dates.append(d)

	return entry



class Condition:
	def isValid():
		return True
class Entry:
	value = "" # string which we should append 
	value_type = "" # red yellow
	dates = []
	raw_value = ""
	label = ""
	def __init__(self):
		self.dates = []
	def __repr__(self):
		return "Entry[raw_value="+ self.raw_value +", value="+self.value +", value_type="+self.value_type +", label=" + self.label + "]" 

def calculateDateFromFixedDate(startdate, weekday, distance):
	weekday = week_days[weekday]
	if distance.startswith("-"):
		return startdate+timedelta(days=(1+weekday + 6-startdate.weekday())%7, weeks=(int(distance)) )
	elif distance.startswith("+"):
		return startdate+timedelta(days=-((7-weekday+ startdate.weekday())%7), weeks=(int(distance)) )
	else:
		return None
		
# month - 1..12 
# weekday - string
# number - first, last, 2nd, 3rd...
def calculateDateByEntry(month, weekday, number): 
	weekday = week_days[weekday]
	
	if "остання" == number:
		days = range(month_sizes[month-1], 0, -1)
		count = 1
	elif "передостання" == number:
		days = range(month_sizes[month-1], 0, -1)
		count = 2
	else:
		days = range(1,month_sizes[month-1]+1)
		count = int(number)
		
	for day in days:
		day_date = date(year,month,day)
		if weekday == day_date.weekday():
			count-=1
			if 0 == count:
				return day_date
	return None

class DateRange:
	startDate = None
	endDate = None
	title = ""
	def __repr__(self):
		return title


class CalendarDate:
	date = None
	saint = ""
	celebr = ""
	additional = ""
	def applyEntry(self, entry):
		if self.date in entry.dates:
			if "sundays" == entry.value_type:
				if self.celebr.endswith(" "):
					self.celebr = self.celebr + entry.value
				else:
					self.celebr = self.celebr +" "+ entry.value
				self.celebr = self.celebr.strip()
			elif "saint" == entry.value_type:
				if self.saint.endswith(" "):
					self.saint = self.saint + entry.value
				else:
					self.saint = self.saint + " " + entry.value
				self.saint = self.saint.strip()
			elif "additional" == entry.value_type:
				if self.additional.endswith(" "):
					self.additional = self.additional + entry.value
				else:
					self.additional = self.additional + " "+ entry.value
				self.additional = self.additional.strip()

def datetime_parser(dct):
	regex = re.compile("^([0-9]{2})/([0-9]{2})$")
	for k, v in dct.items():
		matcher = regex.match(v) # date matcher
		if isinstance(v, str) and None != matcher:
			try:
				dct[k] = date(year, int(matcher.group(1)), int(matcher.group(2)))
			except:
				pass
	return dct

def initCalendar():
	global fixed_dates

	with open("new-style/fixed_dates.json") as file:
		fixed_dates = json.loads(file.read(), object_hook=datetime_parser)
	fixed_dates["Пасха"] = easter_date

	months = range(12)
	for month in months:
		m_days = range(month_sizes[month])
		for day in m_days:
			cal_date = CalendarDate()
			d = date(year, month+1, day +1)
			cal_date.date = d
			days.append(cal_date)
			entry_by_date[d] = [] #{"saint" : [], "sundays": [], "additional": []}

	print(year)
	print(len(days))



def filterEntries():
	for c in conditions:
		if c.entry2 == '*':
			d = date_by_label[c.entry1]
			for entry in list(entry_by_date[d]):
				if entry.label != c.entryToLeave:
					entry_by_date[d].remove(entry)
			continue
		if date_by_label[c.entry1] == date_by_label[c.entry2]:
			d = date_by_label[c.entry1]
			for entry in list(entry_by_date[d]):
				if entry.label in [c.entry1, c.entry2]:
					if entry.label != c.entryToLeave:
						entry_by_date[d].remove(entry)

def applyEntries():
	print("Applying celebrations...")
	for day in days:
		for entry in entry_by_date[day.date]:
			day.applyEntry(entry)

def cleanup():
	for day in days:
		if (day.date == fixed_dates["Різдво"]): #  Christmas so removing everything else
			day.additional = ""
		if (" (на неділю)." in day.additional):
			if (day.date.weekday() == 6 ): # sunday
				day.additional = day.additional.replace(" (на неділю).", ".")
		if day.date == fixed_dates["Пасха"]:
			day.additional = ""
			day.saint = ""

def writeCalendar():
	dir = str(year)
	if not os.path.exists(dir):
		os.makedirs(dir)
	
	total_days_written = 0
	months = range(1,13)

	for month in months:
		month_file = codecs.open(dir + "/" + str(month) + ".ndm", "w", "utf-8-sig")
		month_file.write('\n') #codecs.BOM_UTF8 + '\n')
		month_days_written = 0
		while month_days_written < month_sizes[month-1]:
			day = days[total_days_written + month_days_written]
			month_file.write(str(day.date.day) + "\n")
			month_file.write(day.celebr + "\n")
			month_file.write(day.saint + "\n")
			month_file.write(day.additional + "\n")
			month_file.write("0" + "\n")
			month_file.write("\n")
			month_days_written+=1
		total_days_written+=month_days_written
		month_file.close()
	print (len(days))
	print("Writing calendar to an output file. Done...")

def dateNmonth(date):
	return date.strftime("%-d %B")

def writeHtml():
	months = range(0,12)
	total_days_written = 0
	
	with open('html/template.html', 'r') as template, open('html/'+ str(year) + ".html", 'w') as out:
		for line in template:
			if line.strip() in tokens_to_months:
				month = tokens_to_months[line.strip()]
				month_days_written = 0
				out.write("<table class=\"table table-borderless\"><tbody>")
				while month_days_written < month_sizes[month]:
					day = days[total_days_written + month_days_written]
					
					isCelebr = day.celebr != '' or day.date.weekday() == 6 # sunday
					isSaint = day.saint != ''
					out.write("<tr class=\"month-row "+ ("celebr" if isCelebr else '')+"\">\n")
					out.write("<td class=\"text-right\">\n")
					out.write( str(day.date.day) + "</td>\n")
					out.write("<td>" + week_days_short[day.date.weekday()] + "</td>\n<td>")
					if day.celebr != '':
						out.write("<span class=\" celebr\">" + day.celebr + "</span>\n")
					if isSaint:
						out.write("<span class=\" saint\">" + day.saint + "</span>\n")
					out.write("<span class=\" additional\">" + day.additional + "</span></td>\n")
					out.write("</tr>\n")
					
					month_days_written+=1
				total_days_written+=month_days_written
				out.write("</tbody></table>")
			elif line.strip() == longFastingsToken:
				for f in longFastings:
					out.write(f.title)
					if (f.startDate):
						out.write(" з <span class=\"celebration\">" + dateNmonth(f.startDate))
						if(f.endDate):
							out.write("</span> по <span class=\"celebration\">" + dateNmonth(f.endDate) +"</span><br>")
						else:
							out.write("</span><br>")
					else:
						out.write("<br>")
			elif line.strip() == oneDayFastingsToken:
				for f in oneDayFastings:
					out.write("<span class=\"celebration\">" +dateNmonth(f.startDate) + "</span> - " + f.title + "<br>")
			elif line.strip() == forbiddenTimesToken:
				for f in forbiddenTimes:
					out.write(f.title)
					if (f.startDate):
						out.write(" - <span class=\"celebration\">" + dateNmonth(f.startDate))
						if(f.endDate):
							out.write(" - " + dateNmonth(f.endDate) +"</span><br>")
						else:
							out.write("</span><br>")
					else:
						out.write("<br>")
			elif line.strip() == fastingFreeTimesToken:
				for f in fastFreeTimes:
					out.write("з <span class=\"celebration\">" + dateNmonth(f.startDate) + "</span> по <span class=\"celebration\">" + dateNmonth(f.endDate) + "</span><br>")
			elif line.strip() == "{{year}}":
				out.write(repr(year))
			else:
				out.write(line)
		out.close();
		template.close();

	print (len(days))
	print("Writing calendar to an output file")

initCalendar()
readFastings()
readForbiddenTimes()
readFastFreeTimes()
readSaints()
readCelebr()
readAdditional()
readConditions()
filterEntries()
applyEntries()
cleanup()
writeHtml()
writeCalendar()

