import requests
import schedule
import time
from datetime import datetime
from telegram import Bot

# Данные для интеграции
AMOCRM_BASE_URL = "https://your_subdomain.amocrm.ru"
AMOCRM_ACCESS_TOKEN = "your_amocrm_access_token"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
MANAGERS_CHAT_IDS = {
    "Manager Name 1": "chat_id_1",
    "Manager Name 2": "chat_id_2",
}

bot = Bot(token=TELEGRAM_BOT_TOKEN)


# Получение данных из amoCRM
def get_revenue_data():
    headers = {
        "Authorization": f"Bearer {AMOCRM_ACCESS_TOKEN}"
    }
    # Получение списка сделок
    response = requests.get(f"{AMOCRM_BASE_URL}/api/v4/leads", headers=headers)
    deals = response.json()["_embedded"]["leads"]
    
    # Группировка выручки по менеджерам
    revenue_by_manager = {}
    for deal in deals:
        manager_id = deal["responsible_user_id"]
        price = deal.get("price", 0)
        if manager_id in revenue_by_manager:
            revenue_by_manager[manager_id] += price
        else:
            revenue_by_manager[manager_id] = price
    
    # Получение имен менеджеров
    response_users = requests.get(
        f"{AMOCRM_BASE_URL}/api/v4/users", headers=headers
        )
    users = response_users.json()["_embedded"]["users"]
    manager_names = {user["id"]: user["name"] for user in users}

    # Формирование итогового отчета
    report = {}
    for manager_id, revenue in revenue_by_manager.items():
        manager_name = manager_names.get(manager_id, "Unknown")
        report[manager_name] = revenue

    return report


# Отправка данных в Telegram
def send_daily_report():
    report = get_revenue_data()
    today = datetime.now().strftime("%Y-%m-%d")
    for manager, revenue in report.items():
        message = f"👤 {manager}\n📆 Дата: {today}\n💰 Выручка: {revenue} ₽"
        chat_id = MANAGERS_CHAT_IDS.get(manager)
        if chat_id:
            bot.send_message(chat_id=chat_id, text=message)


# Планирование отправки
schedule.every().day.at("09:00").do(send_daily_report)

if __name__ == "__main__":
    print("Бот запущен. Ожидание времени отправки...")
    while True:
        schedule.run_pending()
        time.sleep(60)
