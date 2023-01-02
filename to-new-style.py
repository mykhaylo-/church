# coding=utf-8
import re,codecs,datetime,os
import locale
from datetime import date, timedelta
import calendar
import json


year = 2003 	# just any not leap year

locale.setlocale(locale.LC_TIME, "uk_UA")

month_sizes = [31, 29 if calendar.isleap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


entry_types = {"місяця":-1,"січня":1,"лютого":2,"березня":3,"квітня":4,"травня":5,"червня":6,"липня":7,"серпня":8,"вересня":9,"жовтня":10,"листопада":11,"грудня":12}
fixedDateRegex = re.compile("^([0-9]{1,2}) (січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)$", re.U)


def dateNmonth(date):
	return date.strftime("%-d %B")

def convertOldStyleToNewStyle():  # the function just subtracts 13 days of the old style date
	with open('old-style/saints.txt', 'r') as oldStyle, open("newStyle.txt", 'w') as newStyle:
		for line in oldStyle:
			fixedDateMatcher = fixedDateRegex.match(line)
			if ( None != fixedDateMatcher):
				if fixedDateMatcher.group(1) == "29" and fixedDateMatcher.group(2) == "лютого":
					newStyle.write(line)
				else:
					oldStyleDate = date(year, int(entry_types[fixedDateMatcher.group(2)]), int(fixedDateMatcher.group(1)))
					newStyleDate = oldStyleDate+timedelta(days=-13)
					newStyle.write(dateNmonth(newStyleDate))
					newStyle.write("\n")
			else:
				newStyle.write(line)

convertOldStyleToNewStyle()
