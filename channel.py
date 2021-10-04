import telebot
import requests
import json
import eventlet
import datetime
import schedule
import time
from dateutil.parser import parse
from datetime import timedelta
from time import sleep

base_url = "https://bugtracking.refocus.ru/"
token = "2043752212:AAH3QyKFLC6LRGNUJFEqHL702DaCkycU6Rg"
auth_token = '3ZEd6XCBdf5vfxfj6Zbuz6FrN4dnY4Kc'
channel_name = "@refocutis"

issues_ids = []

bot = telebot.TeleBot(token)


def get_issues():
	timeout = eventlet.Timeout(100)
	try:
		feed = requests.get(base_url+'api/rest/issues?page_size=20&page=1', headers={'Authorization' : auth_token})
		return json.loads(feed.text)
	except eventlet.timeout.Timeout:
		bot.send_message(channel_name, "Что-то пошло нет так когда я пыталась достать данные из багтрекера", parse_mode='HTML')
		return None
	finally:
		timeout.cancel()

def send_new_posts(items):
	for item in items:
		change = item['history'][-1]['change'] if 'change' in item['history'][-1] else ""
		history = item['history'][-1]['user']['real_name']+" : "+item['history'][-1]['message'] +" : "+ change
		handler = item['handler']['real_name'] if 'handler' in item else "Не назначен"
		text = "<b>"+str(item['id'])+"</b>\n\n"+item['summary']+"\n\n"+history+"\n\n <pre>Инициатор:</pre>"+item['reporter']['real_name']+"\n <pre>Назначен на:</pre>"+handler+"\n <pre>Статус:</pre>"+item['status']['label']+"\n <pre>Приоритет:</pre>"+item['priority']['label']+'\n\n<a href="'+base_url+'view.php?id='+str(item['id'])+'">Подробнее</a>'
		bot.send_message(channel_name, text, parse_mode='HTML')
	time.sleep(1)
	return

def check_new_issues():
	issues = get_issues()
	loaded_issues = []
	new_issues = []

	if issues == None:
		return
	
	current_date = datetime.datetime.now()
	delta = timedelta(minutes=1, seconds=4)
	delta_now = timedelta(hours=current_date.hour,minutes=current_date.minute, seconds=current_date.second)
	
	for issue in issues['issues']:
		delta_issue = timedelta(hours=parse(issue['updated_at']).time().hour,minutes=parse(issue['updated_at']).time().minute, seconds=parse(issue['updated_at']).time().second) + timedelta(hours=3)
		if current_date.date() == parse(issue['updated_at']).date():
			print(delta_now - delta_issue)
			if (delta_now - delta_issue) <= delta :
				new_issues.append(issue)
	print("\n\n")

	# print(new_issues)
	if len(new_issues) > 0 :
		send_new_posts(new_issues) 
	# check_new_issues()
# bot.send_message(channel_name, "Приветсвую Вас.", parse_mode='HTML')

schedule.every(1).minutes.do(check_new_issues)

while True:
    schedule.run_pending()
    time.sleep(1)