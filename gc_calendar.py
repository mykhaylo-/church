# coding=utf-8
import re,codecs,datetime,os
from datetime import date, timedelta
import calendar

year = 2019
fixed_dates = {"Пасха": date(year, 4, 28), "Йордан": date(year,1,19), "Різдво": date(year,1,7), "Іллі": date(year,8,2)}

month_sizes = [31, 29 if calendar.isleap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

entry_types = {"місяця":-1,"січня":1,"лютого":2,"березня":3,"квітня":4,"травня":5,"червня":6,"липня":7,"серпня":8,"вересня":9,"жовтня":10,"листопада":11,"грудня":12}

week_days = {"понеділок":0,"вівторок":1,"середа":2,"четвер":3,"пт":4,"субота":5,"неділя":6}
month_names = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"];
days = []
entry_by_date = {}
date_by_label = {}
conditions = []

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
	readFile("saints.txt", "saint")

def readCelebr():
	print("Read celebr")
	readFile("celebr.txt", "sundays")
	
def readAdditional():
	print("Read additional")
	readFile("add.txt", "additional")

def readConditions():
	file = open("conditions","r")
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

def initCalendar():
	months = range(12)
	for month in months:
		m_days = range(month_sizes[month])
		for day in m_days:
			cal_date = CalendarDate()
			d = date(year, month+1, day +1)
			cal_date.date = d
			days.append(cal_date)
			entry_by_date[d] = [] #{"saint" : [], "sundays": [], "additional": []}

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
		month_file = open(dir + "/" + str(month) + ".ndm", "w")
		month_file.write(codecs.BOM_UTF8 + "\n")
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
	print("Writing calendar to an output file")

def writeHtml():

	out = open(str(year) + ".html", "w")
	out.write(codecs.BOM_UTF8 + "\n")
	out.write("<html><body>")
	out.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"styles.css\" media=\"screen\" />")
	months = range(1,13)
	total_days_written = 0

	for month in months:
		out.write("<h2>" + month_names[month -1] + "</h2>\n")
		month_days_written = 0
		while month_days_written < month_sizes[month-1]:
			day = days[total_days_written + month_days_written]
			
			isCelebr = day.celebr != '' or day.date.weekday() == 6 # sunday
			isSaint = day.saint != ''

			out.write("<div class =\"day "+ ("celebr" if isCelebr else '') + "\">\n")
			out.write("<span class=\"brick\">" + str(day.date.day) + "</span>\n")
			if day.celebr != '':
				out.write("<span class=\"brick celebr\">" + day.celebr + "</span>\n")
			if isSaint:
				out.write("<span class=\"brick saint\">" + day.saint + "</span>\n")
			out.write("<span class=\"brick additional\">" + day.additional + "</span>\n")
			out.write("</div>\n")
			month_days_written+=1
		total_days_written+=month_days_written
	
	out.write("</body></html>\n");

	out.close()
	print (len(days))
	print("Writing calendar to an output file")




initCalendar()
readSaints()
readCelebr()
readAdditional()
readConditions()
filterEntries()
applyEntries()
cleanup()
writeHtml()
#writeCalendar()

