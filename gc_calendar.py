# coding=utf-8
import re,codecs,datetime,os
from datetime import date, timedelta
import calendar

year = 2016
fixed_dates = {"Пасха": date(year, 5, 1), "Йордан": date(year,1,19), "Різдво": date(year,1,7), "Іллі": date(year,8,2)}

month_sizes = [31, 29 if calendar.isleap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

entry_types = {"місяця":-1,"січня":1,"лютого":2,"березня":3,"квітня":4,"травня":5,"червня":6,"липня":7,"серпня":8,"вересня":9,"жовтня":10,"листопада":11,"грудня":12}

week_days = {"понеділок":0,"вівторок":1,"середа":2,"четвер":3,"пт":4,"субота":5,"неділя":6}

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
# def readEntrys():
# 	sectio_re = re.compile("\[([a-z]+)\]")
# 	entry_file = open("entrys","r")
# 	section = ""
# 	while 1:
# 		line1 = entry_file.readline()
# 		if(0 == len(line1)): # EOF
# 			break
# 		if(line1.startswith("#") or 3 > len(line1)): # comment or empty string
# 			continue
# 		matcher = sectio_re.match(line1)
# 		if ( None != matcher):
# 			section = matcher.group(1)
# 			continue
# 		line2 = entry_file.readline().strip()

# 		entry = buildEntryFromLine(line2)
# 		entry.value = line1.strip()
# 		entry.value_type = section

# 		entrys.append(entry)

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
	# if(len(entry_tokens) == 3):
	# 	assert entry_tokens[2] in entry_types
	# 	entry.startpoint = entry_tokens[2]
	# elif(len(entry_tokens) == 4):
	# 	if ("перед" == entry_tokens[2]):
	# 		entry.distance = "-" + entry.distance
	# 	else:
	# 		entry.distance = "+" + entry.distance
	# 	entry.startpoint = entry_tokens[3]
	# elif(len(entry_tokens) > 4):
	# 	entry.startpoint = ' '.join(entry_tokens[3:])

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

		# if day_date == fixed_dates["Пасха"] + timedelta(days=+1):
		# 	self.additional = ""
		# 	self.saint = ""
		# if day_date == fixed_dates["Пасха"] + timedelta(days=+2):
		# 	self.additional = ""
		# 	self.saint = ""


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
# def readCalendarTemplate() :
# 	months = range(1,13)
# 	for month in months:
# 		month_file = open(str(month) + ".ndm", "r")
# 		assert month_file.readline().startswith(codecs.BOM_UTF8)
# 		while 1:
# 			line = month_file.readline()
# 			if(0 == len(line)): # EOF
# 				break
# 			line = line.strip()
# 			cal_date = CalendarDate()
# 			cal_date.month = month
# 			cal_date.day = int(line)
# 			cal_date.celebr = month_file.readline().strip() 
# 			cal_date.saint = month_file.readline().strip()
# 			cal_date.additional = month_file.readline().strip()
# 			cal_date.cross = month_file.readline().strip()
# 			assert 0 == len(month_file.readline().strip())
# 			days.append(cal_date)
# 		assert month_sizes[month-1] == days[-1].day
# 		month_file.close()
				
def filterEntries():
	for c in conditions:
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
#	print(entrys[20])
#	days[4].applyEntry(entrys[20])
#	days[4].applyEntry(entrys[22])

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

# def updateNew():
# 	dir = str(year) + "new"
# 	if not os.path.exists(dir):
# 		os.makedirs(dir)
	
# 	total_days_written = 0
# 	months = range(1,13)

# 	montes = {1:"січня",2:"лютого",3:"березня",4:"квітня", 5:"травня",6:"червня",7:"липня",8:"серпня",9:"вересня",10:"жовтня",11:"листопада",12:"грудня"}

# 	saints_file = open(dir + "/saints.txt", "w")
# 	celebr_file = open(dir + "/celebr.txt", "w")
# 	add_file = open(dir + "/add.txt", "w")

# 	saints_file.write(codecs.BOM_UTF8 + "\n")
# 	celebr_file.write(codecs.BOM_UTF8 + "\n")
# 	add_file.write(codecs.BOM_UTF8 + "\n")

# 	for month in months:
# 		month_days_written = 0
# 		while month_days_written < month_sizes[month-1]:
# 			day = days[total_days_written + month_days_written]

# 			if(day.saint.strip() != ""):
# 				if(day.saint.strip().endswith(".")):
# 					saints_file.write(day.saint.strip() + "\n")
# 				else:
# 					saints_file.write(day.saint.strip() + ".\n")
# 				saints_file.write(str(day.day) + " " + montes[month] + "\n")
# 				saints_file.write("\n")
			
# 			if(day.celebr.strip() != ""):
# 				if(day.celebr.strip().endswith(".")):
# 					celebr_file.write(day.celebr.strip() + "\n")
# 				else:
# 					celebr_file.write(day.celebr.strip() + ".\n")
# 				celebr_file.write(str(day.day) + " " + montes[month] + "\n")
# 				celebr_file.write("\n")
			
# 			if(day.additional.strip() != ""):
# 				if(day.additional.strip().endswith(".")):
# 					add_file.write(day.additional.strip() + "\n")
# 				else:
# 					add_file.write(day.additional.strip() + ".\n")
# 				add_file.write(str(day.day) + " " + montes[month] + "\n")
# 				add_file.write("\n")
			
# 			month_days_written+=1
# 		total_days_written+=month_days_written
# 	print (len(days))

# 	saints_file.close()
# 	celebr_file.close()
# 	add_file.close()
	# print("WritingNEW  calendar to an output file")


initCalendar()
readSaints()
readCelebr()
readAdditional()
readConditions()
filterEntries()
print(entry_by_date[date(year, 1,18)])
# readCalendarTemplate()
applyEntries()
cleanup()
writeCalendar()


