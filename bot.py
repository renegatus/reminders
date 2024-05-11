import telebot
from telebot import types
import logging
from datetime import datetime
import sqlite3
import time
import schedule
import threading

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot("6489457070:AAH8re67vlrTtUnMcDGZmiXkKulMHPhKvFA")

START, SET_REMINDER, WAITING_CONFIRMATION = range(3)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я могу помочь тебе с напоминаниями. Для установки напоминания используй /setreminder.")

@bot.message_handler(commands=['setreminder'])
def set_reminder(message):
    bot.reply_to(message, "Напишите текст напоминания.")
    bot.register_next_step_handler(message, set_reminder_text)

def set_reminder_text(message):
    try:
        reminder_text = message.text
        bot.reply_to(message, "Когда ты хочешь установить напоминание? (Формат: дд-мм-гггг чч:мм)")
        bot.register_next_step_handler(message, set_reminder_time, reminder_text=reminder_text)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

def set_reminder_time(message, reminder_text):
    try:
        reminder_datetime = datetime.strptime(message.text, "%d-%m-%Y %H:%M")
        user_data = {'reminder_text': reminder_text, 'reminder_datetime': reminder_datetime}
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
        bot.send_message(message.chat.id, f"Напоминание установлено на {reminder_datetime.strftime('%d-%m-%Y %H:%M')}. Подтвердить?", reply_markup=markup)
        bot.register_next_step_handler(message, confirmation, user_data=user_data)
    except ValueError:
        bot.reply_to(message, "Некорректный формат. Попробуйте снова.")
        bot.register_next_step_handler(message, set_reminder_time, reminder_text=reminder_text)

def confirmation(message, user_data):
    try:
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        user_input = message.text.lower()
        if user_input == 'да':
            reminder_datetime = user_data['reminder_datetime']
            reminder_text = user_data['reminder_text']
            c.execute("INSERT INTO reminders (chat_id, reminder_text, reminder_datetime) VALUES (?, ?, ?)",
                      (message.chat.id, reminder_text, reminder_datetime.strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            bot.reply_to(message, f"Отлично! Я напомню вам '{reminder_text}' в {reminder_datetime.strftime('%d-%m-%Y %H:%M')}")

        elif user_input == 'нет':
            bot.reply_to(message, "Хорошо, напоминание не установлено.")
        else:
            bot.reply_to(message, "Пожалуйста, ответьте 'Да' или 'Нет'.")
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite: {e}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")



@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.reply_to(message, "Операция отменена.")

def check():
#    try:
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute("SELECT * FROM reminders")
        reminders = c.fetchall()
        for reminder in reminders:
            id, chat_id, reminder_text, reminder_datetime_str = reminder
            reminder_datetime = datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")
            current_time = datetime.now()
            #if carn_time = remender dite то отправить собщений через бот.сендмеседж по айди и удалить запись с напоминанием
            print(f"Chat ID: {chat_id}, Напоминание: {reminder_text}, Дата и время: {reminder_datetime}")
        if current_time >= reminder_datetime:
            bot.send_message(chat_id, f"Напоминание: {reminder_text}")
            c.execute("DELETE FROM reminders WHERE id=?", (id,))
            conn.commit()
            print(f"Отправлено напоминание для chat_id={chat_id}: {reminder_text}")
        else:
            print(f"Напоминание для chat_id={chat_id} еще не пришло время: {reminder_text} ({reminder_datetime})")
        conn.close()
    # except:
    #     print("error")

@bot.message_handler(commands=['clear'])
def clear_database(message):
    try:
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute("DELETE FROM reminders")
        conn.commit()
        conn.close()
        bot.reply_to(message, "История успешно очищена.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite: {e}")
        bot.reply_to(message, "Произошла ошибка при очистке историй.")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        bot.reply_to(message, "Произошла неизвестная ошибка.")



def polling_thread():
    bot.polling(none_stop=True)

def shedule_thread():
    schedule.every().minute.do(check)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    polling_thread = threading.Thread(target=polling_thread)
    polling_shedule = threading.Thread(target=shedule_thread)

    polling_thread.start()
    polling_shedule.start()