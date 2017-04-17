import sqlite3

class Database():
	
	def __init__(self, filepath):
		self.connection = sqlite3.connect(filepath)
		self.connection.execute('''pragma foreign_keys = on;''')
		self.create_tables()
		
	def create_tables(self):
		cursor = self.connection.cursor()
		cursor.execute(''' 
			create table if not exists
			job
				(
				 id integer primary key not null
				,bezeichnung text
				)
			;''')
		cursor.execute('''
		create unique index if not exists
			bez
		on
			job(bezeichnung)
			''')
		cursor.execute(''' 
			create table if not exists
			time_slot
				(
				  id integer primary key not null
				 ,ref_job integer not null
				 ,von timestamp
				 ,bis timestamp
				 
				 ,foreign key(ref_job)
				 references job(id)
				 on delete cascade
				)
			;''')
		self.connection.commit()
	
	def insert_job(self, title):
		cursor = self.connection.cursor()
		inserted_job = cursor.execute('''
			insert into
				job(bezeichnung)
			values
			(?)
			''', (title, )
			)
		job_id = inserted_job.fetchone()
		self.connection.commit()
		return job_id
		
	def update_job(self, term, job_id):
		cursor = self.connection.cursor()
		cursor.execute('''
		update
			job
		set
			bezeichnung = ?
		where
			id = ?
		''', (term, job_id))
		self.connection.commit()
	
	def insert_time(self, begin, end, ref_job):
		cursor = self.connection.cursor()
		cursor.execute('''
		insert into
			time_slot(ref_job, von, bis)
		values
		(?,?,?)
		''', (ref_job, begin, end)
		)
		self.connection.commit()
		
	def get_job_id(self, term):
		cursor = self.connection.cursor()
		job_id = cursor.execute('''
		select
			id
		from
			job
		where
			bezeichnung = ?
		''', (term,))
		job_id = job_id.fetchone()[0]
		cursor.close()
		return job_id
		
	def get_all_job_names(self):
		cursor = self.connection.cursor()
		job_list = cursor.execute('''
		select
			bezeichnung
		from
			job''')
		job_list = [item[0] for item in job_list.fetchall()]
		return job_list
		
	def get_jobs_from_to(self, begin, end):
		cursor = self.connection.cursor()
		jobs_done = cursor.execute('''
		select
			ref_job
		from
			time_slot
		where
			von >= ?
		and
			bis <= ?''', (begin, end))
		self.connection.commit()
	
	def remove_job(self, job_id):
		cursor = self.connection.cursor()
		cursor.execute('''
		delete from
			job
		where
			id = ?
		''', (job_id,))
		self.connection.commit()
