# church-calendar
This is a Python script which generates Greek Catholic calendar of saints.

Repository includes Python script itself and necessary files with data for every day.

To generate calendar correctly you need to specify a year which you want to generate the calendar for and Easter date for that year. So far these parameters are hardcoded at the top of the script.

- saints.txt - this file contains normal ordinary saints which Church mentions with corresponding date
- celebr.txt - this file contains celebrations which needs to be displayed in red.
- add.txt - this file contains additional information which is shown in yellow at the end of day record.
conditions - this file contains "conflicts" resolving strategy, e.g. what to show when collision happens, like Sudays before Lent and Sundays before/after Epiphany. Syntax is following: if labels before colon are on the same date then label after colon wins.
