#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import tkinter as tk
import configparser as cp
import matplotlib.pyplot as plt
import numpy as np
import os, locale, platform, hashlib, tkinter.messagebox, time, datetime, sqlite3

class Wrapper(tk.Frame):
	
	def __init__(self, parent):
		tk.Frame.__init__(self, master=parent)
		self.screen_width = self.master.winfo_screenwidth()
		self.screen_height = self.master.winfo_screenheight()
		self.pack(padx=self.screen_width*0.005, pady=self.screen_height*0.01, anchor=tk.NW)
		self.db_loc = None
		self.conf = None
		self._key = None
		self.loc_window = None
		self.pw_window = None
		self.ask_pw_window = None
		self.setup()
		
	def setup(self):
		self.master.protocol('WM_DELETE_WINDOW', self.close_app)
		self.master.title("Arbeits-Management BETA")
		self.master.geometry('%dx%d+0+0' %(self.screen_width, self.screen_height))
		
		# Set locale depending on OS
		if platform.system() == 'Windows':
			locale.setlocale(locale.LC_ALL, 'deu_deu')
		else:
			locale.setlocale(locale.LC_ALL, 'de_DE')
		
		self.load_db_loc()
		
	def load_db_loc(self):
		
		# Load path to database from config file - or ask user for it, if inexistent
		self.conf = cp.ConfigParser()
		self.conf.read('settings.ini')
		
		def set_db_attribute():
			self.db_loc = loc.get()
			if os.path.isfile(self.db_loc):
				self.conf.set('LOCATIONS', 'db', self.db_loc)
				self.loc_window.destroy()
				self.load_key()
			else:
				tkinter.messagebox.showerror("Fehler", "Die angegebene Datei ist entweder falsch geschrieben, existiert nicht, oder der Pfad dorthin ist fehlerhaft.")
			
		try:
			self.db_loc = self.conf['LOCATIONS']['db']
			if self.db_loc == '':
				raise Exception
			else:
				self.load_key()
		except Exception as e:
			if type(e) == KeyError:
				self.conf.add_section('LOCATIONS')
			self.master.withdraw()
			self.loc_window = tk.Toplevel()
			self.loc_window.title("Datenbank Speicherort")
			tk.Label(self.loc_window, text="Keine Datenbank gefunden.").grid(
					row=0,
					column=0,
					columnspan=2,
					padx=(3,0),
					pady=3
					)
			tk.Label(self.loc_window, text="Bitte vollen Dateipfad der Datenbank angeben:").grid(
					row=1,
					column=0,
					padx=(3,0),
					pady=3
					)
			loc = tk.Entry(self.loc_window, width=50)
			loc.grid(
					row=1,
					column=1,
					padx=(0,3),
					pady=3
					)
			loc.focus_set()
			send = tk.Button(
					self.loc_window,
					text="senden",
					command=set_db_attribute,
					width=30
					)
			send.grid(
					row=2,
					column=0,
					columnspan=2,
					padx=3,
					pady=3
					)
			
	def load_key(self):
		
		# Load hashed password from config file or ask user to enter one and pass it on for hashing
		try:
			self._key = self.conf['GENERAL']['a']
			if self._key == '':
				raise Exception
			else:
				self.compare_pw()
		except Exception as e:
			print(e)
			if type(e) == KeyError:
				self.conf.add_section('GENERAL')
			self.pw_window = tk.Toplevel()
			self.pw_window.title("Passwort setzen")
			tk.Label(self.pw_window, text="Setzen Sie ein Passwort.\nWie üblich sollte es Groß- und Kleinbuchstaben sowie mind. ein Sonderzeichen enthalten").pack()
			pw_entry = tk.Entry(self.pw_window, width=10, show='*')
			pw_entry.pack()
			pw_entry.focus_set()
			tk.Label(self.pw_window, text="Passwort bestätigen:").pack()
			pw_confirm = tk.Entry(self.pw_window, width=10, show='*')
			pw_confirm.pack()
			ok_button = tk.Button(
					self.pw_window,
					text='OK',
					command=lambda: self.set_pw(pw=pw_entry.get(),
					confirm=pw_confirm.get())
					)
			ok_button.pack(pady=10)
			pw_entry.bind('<Return>',lambda event=None: pw_confirm.focus_set())
			pw_confirm.bind('<Return>', lambda pw=pw_entry.get(), confirm=pw_confirm.get():self.set_pw)
		
	def close_app(self):
		
		# User must confirm before closing the application. All changes to config file are saved here; therefor any changes will be lost if the app crashes is closed via terminal kill.
		yesno = tkinter.messagebox.askyesno("Beenden", "Programm wirklich beenden?")
		if yesno:
			with open('settings.ini', 'w') as configfile:
				self.conf.write(configfile)
			self.master.destroy()
		else:
			pass
		
	def set_pw(self, pw, confirm, event=None):
		
		# Hash password and pass it to the config file object
		if pw == confirm:
			password = pw.encode('utf-8')
			key = hashlib.sha256(password).hexdigest()			#No SALT added since this is not intended to be high-level-secure (PW and script are on same machine anyway...)
			self.conf.set('GENERAL', 'a', key)
			self.pw_window.destroy()
			self.master.deiconify()
			MainMenu(self)
			
		else:
			tkinter.messagebox.showerror("Fehler", "Die eingegebenen Passwörter stimmen nicht überein!")
	
	def compare_pw(self):
		
		# Ask user for the password in a dialogue, compare it to the hashed one from config file in a nested function
		
		def check_pw(event=None):
			if self._key == hashlib.sha256(pw_entry.get().encode('utf-8')).hexdigest():
				self.ask_pw_window.destroy()
				self.master.deiconify()
				MainMenu(self)
			else:
				tkinter.messagebox.showerror("Fehler", "Ungültiges Passwort!")
			
		self.master.withdraw()
		self.ask_pw_window = tk.Toplevel()
		self.ask_pw_window.title("Passwort eingeben")
		tk.Label(self.ask_pw_window, text="Geben Sie das Passwort für die Benutzung des Programms ein:").pack()
		pw_entry = tk.Entry(self.ask_pw_window, width=10, show='*')
		pw_entry.pack(pady=3)
		pw_entry.focus_set()
		pw_entry.bind('<Return>', check_pw)
		ok_button = tk.Button(self.ask_pw_window, text='OK', command=check_pw)
		ok_button.pack(pady=5)
		
class MainMenu(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, master=parent, bd=2, relief=tk.GROOVE)
		self.grid(
				row=0,
				column=0,
				padx=int(parent.screen_width*0.005),
				pady=int(parent.screen_height*0.01),
				sticky=tk.NW
				)
		self.parent = parent
		self.current_date = tk.StringVar()
		self.date_label = tk.Label(self,
				textvariable=self.current_date,
				font=('Segoe UI', 14, 'bold')
				).pack(padx=7)
		self.load_date_window = None
		self.calendar = None
		self.db = Database()
		
		self.set_date(datetime.datetime.today())
		self.place_buttons()
		
	def calculate_hours(self):
		
		# Calculate a timestamp as string for each quarter of an hour between 07:00 and 21:00 (format: HH:MM)
		start_time = datetime.datetime(100, 1, 1, 6, 45)
		hours =[]
		for x in range(60):
			start_time += datetime.timedelta(seconds=900)
			time_formatted = start_time.time().strftime('%H:%M')
			hours.append(str(time_formatted))
		return(hours)
		
	def set_date(self, date):
		self.current_date.set(date.strftime('%A, %d. %B %Y'))
		self.calendar = Calendar(self.parent, self.calculate_hours(), self.db.job_tiles())
		self.calendar.fill_in_jobs(self.db.load_jobs(date.date()))
	
	def change_date(self):
		
		# Ask user for a date, which will be displayed at the top of the main menu
		def replace_date():
			date = datetime.datetime.strptime(day.get()+month.get()+year.get(), '%d%m%Y')
			self.set_date(date)
			self.load_date_window.destroy()
		self.load_date_window = tk.Toplevel()
		self.load_date_window.title("Datum laden")
		tk.Label(self.load_date_window, text="Datum spezifizieren:").grid(
				row=0,
				column=0,
				columnspan=3,
				padx=3,
				pady=3
				)
		day = tk.StringVar()
		month = tk.StringVar()
		year = tk.StringVar()
		tk.Label(self.load_date_window, text="Tag").grid(row=1, column=0)
		tk.Label(self.load_date_window, text="Monat").grid(row=1, column=1)
		tk.Label(self.load_date_window, text="Jahr").grid(row=1, column=2)
		day_menu = tk.OptionMenu(self.load_date_window, day, *list(range(1,32)))
		day_menu.grid(row=2, column=0)
		month_menu = tk.OptionMenu(self.load_date_window, month, *list(range(1,13)))
		month_menu.grid(row=2, column=1)
		year_menu = tk.OptionMenu(self.load_date_window, year, *list(range(2016,2037)))
		year_menu.grid(row=2, column=2)
		tk.Button(self.load_date_window,
				text="senden",
				command=replace_date,
				width=15, height=2).grid(
						row=3,
						column=0,
						columnspan=3,
						pady=3
						)
						
	def save_data(self):
		result = self.db.save_jobs_to_db(
				self.current_date.get(),
				self.calendar.convert_textItemID_to_txt()
				)
		if result == 1:
			tkinter.messagebox.showinfo("Acta sunt reposita!", "Die heutigen Arbeiten wurden erfolgreich gespeichert.")
			self.set_date(datetime.datetime.strptime(self.current_date.get(), '%A, %d. %B %Y'))
		else:
			tkinter.messagebox.showinfo("Speicherfehler", "Möglicherweise ist beim Speichern der Arbeiten ein Fehler aufgtreten.\nBitte überprüfen Sie die Daten.")
			
	def add_job(self):
		
		# GUI dialogue: user enters job title
		def submit(event=None):
			self.db.add_job(name.get())
			self.calendar.draw_jobs(name.get())
			jobtile_window.destroy()
			
		jobtile_window = tk.Toplevel()
		tk.Label(jobtile_window, text="Bezeichnung: ").pack(
				side=tk.LEFT,
				pady=5,
				padx=(5,0)
				)
		name = tk.Entry(jobtile_window, width=30)
		name.pack(side=tk.LEFT, pady=5, padx=(0,5))
		name.focus_set()
		name.bind('<Return>', submit)
		tk.Button(jobtile_window,
				text="OK",
				command=submit,
				width=4,
				height=2
				).pack(side=tk.BOTTOM, pady=3, padx=5)
				
	def remove_job(self):
		
		# GUI dialogue: User selects job to remove from dropdown list
		def submit():
			self.db.delete_job(job_shown.get())
			self.calendar.remove_jobtile(job_shown.get())
			rem_window.destroy()
			tkinter.messagebox.showinfo("Erfolg", "Die Tätigkeit wurde erfolgreich entfernt.")
			
		job_shown = tk.StringVar()
		rem_window = tk.Toplevel()
		rem_window.title("Job entfernen")
		tk.Label(rem_window, text="Welche Tätigkeit wollen Sie entfernen?").pack(
				padx=5,
				pady=5
				)
		job = tk.OptionMenu(rem_window, job_shown, *self.db.job_tiles()).pack(
				padx=5,
				pady=5
				)
		ok_button = tk.Button(
				rem_window,
				text="OK",
				command=submit,
				width=3,
				height=2
				)
		ok_button.pack(
				padx=5,
				pady=5
				)
	
	def ask_date_pdf(self):
		
		# Ask User for a start and end date. All dates in between will be printed in a pdf.
		
		def submit():
			try:
				start_date = datetime.datetime.strptime(start_day.get()+start_month.get()+start_year.get(), '%d%m%Y')
				end_date = datetime.datetime.strptime(end_day.get()+end_month.get()+end_year.get(), '%d%m%Y')
				if end_date < start_date:
					raise ArithmeticError
				else:
					PrintPdf(start_date, end_date)
			except ValueError as e:
				text = "Beide Datumsfelder müssen vollständig ausgefüllt sein!\nFehlerbeschreibung:\n" + str(e)
				tkinter.messagebox.showerror("Fehler", text)
			except ArithmeticError:
				tkinter.messagebox.showerror("Fehler", "Das eingegebene Enddatum liegt vor dem Startdatum. Bitte geben Sie ein korrektes End-/Startdatum ein!")
				
		pdf_window = tk.Toplevel()
		pdf_window.title("Tagessätze auswählen")
		tk.Label(pdf_window, text="Wählen Sie unten die Tage aus, die als Auswertung im pdf erscheinen sollen\n(Von - bis)").grid(row=0, column=0, columnspan=3)
		tk.Label(pdf_window,text="Tag", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0)
		tk.Label(pdf_window,text="Monat", font=('Segoe UI', 10, 'bold')).grid(row=1, column=1)
		tk.Label(pdf_window,text="Jahr", font=('Segoe UI', 10, 'bold')).grid(row=1, column=2)
		days_allowed = list(range(1,32))
		months_allowed = list(range(1,13))
		years_allowed = list(range(2016,2037))
		
		# Start date
		start_day = tk.StringVar()
		start_month = tk.StringVar()
		start_year = tk.StringVar()
		start_day_menu = tk.OptionMenu(pdf_window, start_day, *days_allowed)
		start_day_menu.grid(row=2, column=0)
		start_month_menu = tk.OptionMenu(pdf_window, start_month, *months_allowed)
		start_month_menu.grid(row=2, column=1)
		start_year_menu = tk.OptionMenu(pdf_window, start_year, *years_allowed)
		start_year_menu.grid(row=2, column=2)
		
		# End date
		end_day = tk.StringVar()
		end_month = tk.StringVar()
		end_year = tk.StringVar()
		end_day_menu = tk.OptionMenu(pdf_window, end_day, *days_allowed)
		end_day_menu.grid(row=3, column=0)
		end_month_menu = tk.OptionMenu(pdf_window, end_month, *months_allowed)
		end_month_menu.grid(row=3, column=1)
		end_year_menu = tk.OptionMenu(pdf_window, end_year, *years_allowed)
		end_year_menu.grid(row=3, column=2)
		
		tk.Button(pdf_window,
				text="senden",
				command=submit,
				width=15,
				height=3
				).grid(row=4, column=0, columnspan=3, pady=5)
		
	def place_buttons(self):
		
		# Site all the buttons
		button_quit = tk.Button(
				self,
				text="Programm beenden",
				command=main_window.close_app,
				height=2,
				width=int(main_window.screen_width*0.011),
				font=('Segoe UI', 12, 'bold'),
				bg='red',
				fg='white'
				)
		button_quit.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01)
				)
		button_print = tk.Button(
				self,
				text="PDF erzeugen",
				command=self.ask_date_pdf,
				width=int(main_window.screen_width*0.011),
				font=('Segoe UI', 12, 'bold'),
				bg='#54a3f3')
		button_print.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01)
				)
		button_load_date = tk.Button(
				self,
				text="Datum laden",
				command=self.change_date,
				width=int(main_window.screen_width*0.011),
				font=('Segoe UI', 12, 'bold'),
				bg='#54a3f3'
				)
		button_load_date.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01)
				)
		button_save_jobs = tk.Button(
				self,
				text="Speichern",
				command=self.save_data,
				width=int(main_window.screen_width*0.011),
				font=('Segoe UI', 12, 'bold'),
				bg='#54a3f3'
				)
		button_save_jobs.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01)
				)
		button_open_stats = tk.Button(
				self,
				text="Statistik öffnen",
				command=Statistics,
				width=int(main_window.screen_width*0.011),
				font=('Segoe UI', 12, 'bold'),
				bg='#54a3f3'
				)
		button_open_stats.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01),
				)
		button_add_job = tk.Button(
				self,
				text="+",
				command=self.add_job,
				width=int(main_window.screen_width*0.010),
				font=('Segoe UI', 14, 'bold'),
				bg='#93c120'
				)
		button_add_job.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01),
				)
		button_remove_job = tk.Button(
				self,
				text=u"\u2013",
				command=self.remove_job,
				width=int(main_window.screen_width*0.010),
				font=('Segoe UI', 14, 'bold'),
				bg='#e44040'
				)
		button_remove_job.pack(
				pady=int(main_window.screen_height*0.01),
				padx=int(main_window.screen_width*0.01),
				)
		
		
class Statistics():
	''' Calculates statistics about the spent worktime. Draws graphs using matplotlib '''
	def __init__(self):
		self.db = Database()
		self.dates = self.db.load_all_dates()
		self.select_time()
		
	def totalise_work(self, start, start_form, end, end_form):
		work_dates = []
		hours_per_day = []
		hours_counter = 0	# Sum of quarters of an hour that have been worked during the given time period.
		for x in self.dates:
			formatted = datetime.datetime.strptime(x, '%Y-%m-%d')
			if start_form <= formatted <= end_form:
				work_dates.append(x)
		for y in work_dates:
			jobs = self.db.load_jobs(y)
			increment = [z for z in jobs if z]
			hours_counter += len(increment)/4
			hours_per_day.append(len(increment)/4)
		self.draw_graph(work_dates, hours_per_day, hours_counter)
		
	def draw_graph(self, dates, hours, sum_hours):
		x = 'Gesamt: ' + str(sum_hours)
		ticker = [x for x in range(len(dates))]
		fig = plt.figure()
		fig.suptitle(x)
		axes = fig.gca()
		axes.set_xticks(np.arange(0,float(len(dates)),1))
		axes.set_yticks(np.arange(0,float(len(hours)),0.25))
		axes.set_xticklabels(dates)
		axes.set_xlabel('Datum')
		axes.set_ylabel('Gearbeitete Stunden')
		plt.plot(ticker, hours)
		plt.plot(ticker, hours, 'ob')
		plt.grid()
		plt.show()
			
	def select_time(self):
		
		def convert_and_submit():
			start_formatted = datetime.datetime.strptime(start_date.get(), '%Y-%m-%d')
			end_formatted = datetime.datetime.strptime(end_date.get(), '%Y-%m-%d')
			if start_formatted < end_formatted:
				params = [start_date.get(),start_formatted, end_date.get(), end_formatted]
				select_dates_window.destroy()
				self.totalise_work(params[0], params[1], params[2], params[3])
			else:
				tkinter.messagebox.showerror("Fehler", "Das Startdatum muss vor dem Enddatum liegen!")
				select_dates_window.lift()
			
		start_date = tk.StringVar()
		end_date = tk.StringVar()
		select_dates_window = tk.Toplevel()
		select_dates_window.title("Start- und Enddatum eingeben")
		tk.Label(select_dates_window, text="Startdatum wählen:").grid(
				row=0,
				column=0,
				padx=3,
				pady=3
				)
		select_start = tk.OptionMenu(
				select_dates_window,
				start_date,
				*self.dates
				)
		select_start.grid(
				row=0,
				column=1,
				padx=1,
				pady=3
				)
		tk.Label(select_dates_window, text="Enddatum wählen:").grid(
				row=1,
				column=0,
				padx=3,
				pady=3
				)
		select_end = tk.OptionMenu(
				select_dates_window,
				end_date,
				*self.dates
				)
		select_end.grid(
				row=1,
				column=1,
				padx=1,
				pady=3
				)
		submit = tk.Button(
				select_dates_window,
				text = "senden",
				command=convert_and_submit,
				)
		submit.grid(
				row=2,
				column=0,
				columnspan=2,
				padx=3,
				pady=3,
				sticky='nsew'
				)
		
class Calendar(tk.Canvas):
	''' Used to display the calendar and provide the corresponding drag-and-drop functionality.'''
	def __init__(self, parent, hours, jobs):
		tk.Canvas.__init__(
				self,
				master=parent,
				width=int(parent.screen_width*0.5),
				height=int(parent.screen_height*0.8),
				bd=2,
				relief=tk.GROOVE)
		self.grid(
				row=0,
				column=1,
				padx=int(parent.screen_width*0.005),
				pady=int(parent.screen_height*0.01),
				sticky=tk.NW
				)
		self.parent = parent
		self.update()				# Clear the viewport: if user has dropped jobs and then loads another date, the dropped tiles would remain. This must not be the case for the new date, so we make sure old tiled are removed beforehand.
		self.parent.update()		# We need this for the correct calculation of the window size. The canvas has to be rendered before winfo_size() works
		self.hours = hours
		self.canvas_items = {}		# Format: field<number> : (4 coords), 'hh:mm', canvas item id for rectangle
		self.rectangles_used = {}	# Format: rectangle_ID : ID_of_Textitem_Above
		self.jobs_fulfilled = {}	# Format: 'hh:mm' : ID_of_Textitem
		self.calendar_grid()
		for job in jobs:
			self.draw_jobs(job)
				
	def calendar_grid(self):
		
		# Draw the grid for the jobtiles to be dragged upon. One cell stands for a quarter of an hour.
		max_height = self.winfo_height()-10 # Height allowed for rectangle area: canvas minus padding
		rect_height = max_height/16.5		# Value (16.5) is made out of 15 rows plus one row for quarter-hour-labelling, plus some padding
		rect_width = self.winfo_width()*0.1
		x1 = self.winfo_width()*0.35
		x2 = x1+rect_width
		y1 = 60
		quarters = ['bis :15', 'bis :30', ' bis:45', 'bis :00 n. Std.']
		counter = 0
		
		def draw_rect(counter):
			x1_local = x1
			x2_local = x2
			for y in range(4):
				if counter < 4:	# That is: on first call. Used to draw a text line above the table.
					self.create_text(
							x1_local+rect_width*0.5,
							y1-rect_height*0.5,
							text=quarters[y],
							font=('Segoe UI', 12, 'bold')
							)
				rect = self.create_rectangle(x1_local, y1, x2_local, y1+rect_height)
				self.canvas_items.update(
						{'field'+str(counter):(self.bbox(rect), self.hours[counter], rect)}
						)
				counter += 1
				x1_local += rect_width
				x2_local += rect_width
			return counter
		
		for index in range(14):
			self.create_text(
					x1-rect_width*0.5,	# X-Position
					y1+rect_height*0.5,	# Y-position
					width=int(self.winfo_width()*0.2),
					text=self.hours[counter],
					font=('Segoe UI', 12, 'bold')
					)
			counter = draw_rect(counter)
			y1 += rect_height+2
			self.create_text(
					x2+rect_width*3.5,	# X-position
					y1-rect_height*0.5,	# Y-position
					width=int(self.winfo_width()*0.2),
					text=self.hours[counter],
					font=('Segoe UI', 12, 'bold')
					)
					
	def draw_jobs(self, job):
		
		# List all jobs that exist in the database (as text) so they can be draged and dropped
		if job == None:
			return		#If table "jobs" does not exist, the argument 'name' is None. This may be the case at the very first start of the program - in order to avoid an exception, we simply skip this method in that case.
				
		x1=10
		x2=11
		y1=75
		y2=76
		while True:
			overlapping_item = self.find_overlapping(x1,y1,x2,y2)
			if overlapping_item:
				y1 += 13
				y2 += 13
			else:
				break
			
		tile = self.create_text(
				x1,	# X-position
				y2,	# Y-position
				text=job,
				font=('Segoe UI', 12, 'bold'),
				fill='blue',
				anchor=tk.NW,
				width=int(self.parent.screen_width*0.1)
				)
		self.canvas_items.update({job:tile})
		self.tag_bind(tile, '<ButtonPress-1>', self.copy_tile)
		self.tag_bind(tile, '<B1-Motion>', self.move_tile)
		self.tag_bind(tile, '<ButtonRelease-1>', self.drop_tile)
		last_bbox = self.bbox(tile)
			
	def copy_tile(self, event):
		
		# On click onto the jobtext, it is doubled - this double will then be moved around
		double = self.create_text(
				event.x,
				event.y,
				text=self.itemcget(tk.CURRENT, 'text'),
				font=('Segoe UI', 12, 'bold'),
				fill='blue',
				anchor=tk.NW,
				width=int(self.parent.screen_width*0.1)
				)
		self.canvas_items.update({'double':double})
		
	def move_tile(self, event):
		
		# Moves the doubled jobtile around
		self.coords(self.canvas_items['double'], event.x, event.y)
		
	def drop_tile(self, event):
		
		# Handles the changes to the grid when dropping a job inside a cell - a little weird to read because of the canvas item-IDs stored in self.canvas_items
		for key in self.canvas_items:
			if 'field' in key:
				field_coords = self.canvas_items[key][0]
				double_coords = self.coords(self.canvas_items['double'])
				if field_coords[0] <= double_coords[0] <= field_coords[2] and field_coords[1] <= double_coords[1] <= field_coords[3]: # Overlap-check without Tkinter's find_overlapping(), which proved not useful in this context. Overlapping is detected by upper left coords of the jobtile, which is always (even in the case of very, very long jobtiles) unique.
					if self.canvas_items[key][2] in self.rectangles_used:
						self.delete(self.rectangles_used[self.canvas_items[key][2]])
					self.itemconfig(self.canvas_items[key][2], fill='green')
					txt_shown = self.create_text(
							field_coords[0]+2,	# X-position
							field_coords[1]+2, 	# Y-position
							text=self.itemcget(self.canvas_items['double'],'text'),
							width=field_coords[2]-field_coords[0],
							font=('Segoe UI', 10),
							fill='white',
							anchor=tk.NW
							)
					self.rectangles_used.update({self.canvas_items[key][2]:txt_shown})	# Store ID of used rectangle (as key) and canvas textitem for later reference
					self.jobs_fulfilled[self.canvas_items[key][1]] = txt_shown
		self.delete(self.canvas_items['double'])
		self.clear_rect_event_bindings()
		
	def convert_textItemID_to_txt(self):
		
		# Transforms the tk.Canvas.textitem ID to the respective item's text. The latter must be stored in the database for later identification.
		converted_dict = {time:self.itemcget(job, 'text') for time, job in self.jobs_fulfilled.items()}
		print(converted_dict)
		return converted_dict
		
	def fill_in_jobs(self, jobs):
		
		if not jobs:
			return	# If the function loading the jobs from the db returns nothing (none), this function is obsolete and can skip
		for index, value in enumerate(jobs):
			if value:	# value is None if no job was saved at a particular time.
				y = self.hours[index]
				for key, field in self.canvas_items.items():
					try:
						if y in field:
							self.itemconfig(self.canvas_items[key][2], fill='green')
							txt_shown = self.create_text(
									self.canvas_items[key][0][0]+2,		# X-position
									self.canvas_items[key][0][1]+2, 	# Y-position
									text=value,
									width=self.canvas_items[key][0][2]-self.canvas_items[key][0][0],
									font=('Segoe UI', 10),
									fill='white',
									anchor=tk.NW
							)
							self.rectangles_used.update({self.canvas_items[key][2]:txt_shown})
							self.jobs_fulfilled.update({y:value})
					except:
						continue	# self.canvas_items also contains the canvas item id of the text doubles (see above) as int. Since they can't be iterated over, we have to skip the loop in that case.
				self.clear_rect_event_bindings()
				
	def remove_jobtile(self, name):
		
		# Delete the given jobtile
		self.delete(self.canvas_items[name])
		
	def clear_rect_event_bindings(self):
		
		# Some event bindings for better usability and the removal of dropped jobtiles
		def fill(event=None):
			self.itemconfig(txt, activefill='#76bd18')
			
		def delete(event=None):
			
			current_job = self.find_withtag(tk.CURRENT)[0]
			for key, value in self.rectangles_used.items():
				if value == current_job:
					# Delete selected job from dict self.jobs_fulfilled by VALUE: rewrite dict
					self.jobs_fulfilled = {
							hour:job
							for hour, job
							in self.jobs_fulfilled.items()
							if value != job
							}
					del self.rectangles_used[key]
					self.delete(tk.CURRENT)
					self.itemconfig(key, fill='')
					break
			
		for rect, txt in self.rectangles_used.items():
			self.tag_bind(txt, '<Enter>', fill)
			self.tag_bind(txt, '<Button-3>', delete)
			
class Database():
	''' Handles all actions related to the underlying SQLite database such as storing, loading and saving data, as well as returning them using the defined interface. '''
	def __init__(self):
		self.database = sqlite3.connect(main_window.db_loc)
		self.c = self.database.cursor()
		
	
	def save_jobs_to_db(self, date, jobs_fulfilled):
		
		# Takes a date and the respectively fulfilled jobs, formats the date and inserts it as a unique key to the database (if yet inexistent). Otherwise, it updates the given date or (if even the whole table is missing) creates the table first.
		current_date = datetime.datetime.strptime(date, '%A, %d. %B %Y').date()
		def write_values():
			for x in jobs_fulfilled:
				job = jobs_fulfilled[x]
				if job == '':	# This is true if the user deleted a dropped job by right clicking it. This leaves the former index in jobs_fulfilled with an empty string, which would mess up the statistics: it counts every cell of the database that is not None - even if the string is empty.
					job = None
				x = x.replace(':', '_')
				x = x.replace(' ', '')
				x = x.replace('-', '')
				x = 'b' + x
				self.c.execute('''UPDATE finishedJobs SET %s = ? where date = ?''' % x, (job, current_date))
			self.database.commit()
			return(1)
		try:		# This is split for correction/update purposes, because changes/several "save"-actions are likely. See also below.
			self.c.execute('''INSERT INTO finishedJobs (date) VALUES (?) ''', (current_date, ))
			writing = write_values()
			return writing
		except sqlite3.IntegrityError:
			#if the primary key (i.e. the date) already exists, we can skip the insertion and continue with inserting/update the values for this key
			writing = write_values()
			return writing
		except sqlite3.OperationalError:
			self.c.execute('''CREATE TABLE finishedJobs (date text PRIMARY KEY, b07_00, b07_15, b07_30, b07_45, b08_00, b08_15, b08_30, b08_45, b09_00, b09_15, b09_30, b09_45, b10_00, b10_15, b10_30, b10_45, b11_00, b11_15, b11_30, b11_45, b12_00, b12_15, b12_30, b12_45, b13_00, b13_15, b13_30, b13_45, b14_00, b14_15, b14_30, b14_45, b15_00, b15_15, b15_30, b15_45, b16_00, b16_15, b16_30, b16_45, b17_00, b17_15, b17_30, b17_45, b18_00, b18_15, b18_30, b18_45, b19_00, b19_15, b19_30, b19_45, b20_00, b20_15, b20_30, b20_45, b21_00)''')
			self.database.commit()
			self.save_jobs_to_db(date, jobs_fulfilled)
		
	def job_tiles(self):
		
		# Picks all available jobs from the database and returns them
		try:
			tiles = self.c.execute('''SELECT * FROM jobs''')
			tiles_new = [x[0] for x in tiles]
			return(list(tiles_new))
		except:
			self.c.execute('''CREATE TABLE jobs(name)''')
			self.database.commit()
			
	def delete_job(self, job):
		
		# Deletes the given job from the database; the jobtile on the canvas has already been removed in another function
		self.c.execute('''DELETE FROM jobs WHERE name=?''', (job,))
		self.database.commit()
		
	def add_job(self, job):
		
		# Adds the given job to the database.
		self.c.execute('''INSERT INTO jobs VALUES (?)''', (job,))
		self.database.commit()
		
	def load_jobs(self, date):
		
		# Try to load jobs from the database at a given date - if there are none, the function will skip
		try:
			jobs = self.c.execute ('''SELECT * FROM finishedJobs WHERE date=?''', (date,)).fetchone()
			jobs = list(jobs)
			del jobs[0]
			return jobs
		except:
			return
			
	def load_all_dates(self):
		
		try:
			dates = self.c.execute('''SELECT date FROM finishedJobs''').fetchall()
			dates = [x[0] for x in dates]
			return dates
		except:
			return
		
class PrintPdf():
	''' Prints data to pdf files by requesting it from the database (using the interface class) and formatting it, using the module Reportlab.
	
	Reportlab has some known side effects and bugs likely restricting further options. For example, no single compiler for Python executables (either on Mac or Win)
	works with Reprtlab.  '''
	def __init__(self, start_date, end_date):
		self.start_date = start_date
		self.end_date = end_date
		self.db = Database()
		self.get_jobs()
		
		# Plan für diese Klasse: im MainMenu wird der Nutzer nach einem Start- und Enddatum gefragt. Die zugehörige GUI wird über eine Methode innerhalb von MainMenu bereitgestellt. Der Sendenbutton dieses GUI Dialogs erzeugt dann ein printPdf Objekt mit den beiden Daten als Parameter. Die PrintPdf Klasse hat per se drei Jobs: mittels Start- und Enddatum die Daten aus der Datenbank laden, dazu ein neues DB-Obejkt erzeugen. Wir können hierzu die bereits vorhandene methode Load_jobs nutzen; diese muss auf dem neuen Objekt für jedes Datum zwischen Start und Ende aufgerufen und der Rückgabewert in einer nested list gespeichert werden (Jeder Tag eine Liste mit Jobs und alle Tage als Gesamtliste). Zweitens: das Reportlab framework initiieren; füe jeden Tag mit Arbeiten eine Minitabelle erstellen und diese in die flowables Liste einhängen. Die Miniliste wird in einer eigenen Subklasse von printPdf erstellt und formatiert. Diese Subklasse wird vsl. eine Methode erhalten, die dann die fertige Tabelle zurückliefert: wir instanziieren also einmal ein Tabellen-Subklassenobjekt und rufen dann darauf die Methode zur Rückgabe der Tabelle für jeden Tag auf. Das ist zwat etwas umsätndlich, dafür kann die Formatierung der Tabelle sauber angepasst oder erweitert werden, ohne dass der Rest der Reportlab Klasse btroffen wäre.
	def get_jobs(self):
		time_span = self.end_date - self.start_date
		

if __name__ == '__main__':
	root = tk.Tk()
	main_window = Wrapper(root)
	main_window.mainloop()
