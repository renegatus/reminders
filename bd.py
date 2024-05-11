import sqlite3

conn = sqlite3.connect('reminders.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS reminders
             (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, reminder_text TEXT, reminder_datetime TEXT)''')


conn.commit()

conn.close()
