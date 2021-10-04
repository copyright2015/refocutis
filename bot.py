
import telebot
import requests
import json
import datetime
from dateutil.parser import parse
import subprocess as sp

base_url = "https://bugtracking.refocus.ru/"
token = "2043752212:AAH3QyKFLC6LRGNUJFEqHL702DaCkycU6Rg"
auth_token = '3ZEd6XCBdf5vfxfj6Zbuz6FrN4dnY4Kc'
channel_name = "@refocutis"

channel_process = None

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Привет! Я Refocutis. Я буду оповещать вас об активности задач в нашем багтрекере. \n Рекомендую сразу выполнить команду /channel и подписаться на канал.")

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Доступные команды: \n /dayly - Список активных задач за сегдня(максимум 20); \n /latest - 5 последних активных задач \n /channel - канал где будут поститься активные тикеты; \n /start_channel - запустить процесс обработки уведомлений об активности задач; \n /stop_channel - остановить процесс сбора данных для канала;")

@bot.message_handler(commands=['latest'])
def send_latest(message):
	result = requests.get(base_url+'api/rest/issues?page_size=5&page=1', headers={'Authorization' : auth_token})

	issues = json.loads(result.text)
	
	for item in issues['issues']:
		change = " : " +item['history'][-1]['change'] if 'change' in item['history'][-1] else ""
		history = item['history'][-1]['user']['real_name']+" : "+item['history'][-1]['message'] + change
		handler = item['handler']['real_name'] if 'handler' in item else "Не назначен"
		text = "<b>"+str(item['id'])+"</b>\n\n"+item['summary']+"\n\n"+history+"\n\n <pre>Инициатор:</pre>"+item['reporter']['real_name']+"\n <pre>Назначен на:</pre>"+handler+"\n <pre>Статус:</pre>"+item['status']['label']+"\n <pre>Приоритет:</pre>"+item['priority']['label']+'\n\n<a href="'+base_url+'view.php?id='+str(item['id'])+'">Подробнее</a>'
		bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['dayly'])
def send_daylyes(message):
	result = requests.get(base_url+'api/rest/issues?page_size=20&page=1', headers={'Authorization' : auth_token})

	issues = json.loads(result.text)
	
	current_date = datetime.datetime.now()

	for item in issues['issues']:
		if current_date.date() == parse(issue['updated_at']).date():
			change = item['history'][-1]['change'] if 'change' in item['history'][-1] else ""
			history = item['history'][-1]['user']['real_name']+" : "+item['history'][-1]['message'] +" : "+ change
			handler = item['handler']['real_name'] if 'handler' in item else "Не назначен"
			text = "<b>"+str(item['id'])+"</b>\n\n"+item['summary']+"\n\n"+history+"\n\n <pre>Инициатор:</pre>"+item['reporter']['real_name']+"\n <pre>Назначен на:</pre>"+handler+"\n <pre>Статус:</pre>"+item['status']['label']+"\n <pre>Приоритет:</pre>"+item['priority']['label']+'\n\n<a href="'+base_url+'view.php?id='+str(item['id'])+'">Подробнее</a>'
			bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['channel'])
def send_welcome(message):
	bot.reply_to(message, "Подпишитесь на канал https://t.me/refocutis")

@bot.message_handler(commands=['start_channel'])
def start_channel(message):
	global channel_process
	if(channel_process == None):
		channel_process = sp.Popen(['python','channel.py'])
		bot.reply_to(message, "Я готова собирать для вас информацию о задачах")
	else:
		bot.reply_to(message, "Я уже работаю")

@bot.message_handler(commands=['stop_channel'])
def stop_channel(message):
	global channel_process
	if(channel_process != None):
		sp.Popen.terminate(channel_process)
		channel_process = None
		bot.reply_to(message, "Отдыхаем")
	else:
		bot.reply_to(message, "Я уже отдыхаю")

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	bot.reply_to(message, message.text)
if(channel_process == None):
	channel_process = sp.Popen(['python','channel.py'])
	bot.send_message(channel_name, "Приветсвую Вас)", parse_mode='HTML')
else:
	pass


bot.infinity_polling()







