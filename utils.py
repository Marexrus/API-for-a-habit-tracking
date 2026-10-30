from datetime import *

def current_date():
  return date.today().strftime('%d-%m-%y')

def current_datetime():
  return datetime.today().strftime('%d-%m-%y %H:%M')

def calculate_streaks(dates: list[datetime]) -> tuple[int, int]:
    if not dates:
        return 0, 0

    # Убираем повторы, оставляем только даты
    days = sorted(set(dt.date() for dt in dates))

    # Считаем максимальную серию
    max_streak = 1
    streak = 1

    for i in range(1, len(days)):
        if days[i] == days[i - 1] + timedelta(days=1):
            streak += 1
        else:
            streak = 1

        max_streak = max(max_streak, streak)

    # Считаем текущую серию
    today = date.today()
    current_streak = 0

    # Серия актуальна, если привычка выполнялась сегодня
    # или вчера (если сегодня ещё не отмечена)
    last_day = days[-1]

    if last_day >= today - timedelta(days=1):
        current_streak = 1

        for i in range(len(days) - 1, 0, -1):
            if days[i] - days[i - 1] == timedelta(days=1):
                current_streak += 1
            else:
                break

    return current_streak, max_streak