from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)  # Разрешаем запросы отовсюду

# Здесь будем хранить список игроков на кик
# Это как список покупок: кто, когда и за что
kick_queue = {}

# === ЭТОТ АДРЕС БУДЕТ ОПРАШИВАТЬ ТВОЙ ROBLOX СКРИПТ ===
@app.route('/poll', methods=['GET'])
def poll_server():
    """Сюда Roblox будет стучаться каждые 10 секунд"""
    
    # Проверяем, есть ли кого кикать прямо сейчас
    current_time = datetime.now()
    tasks_to_execute = []
    
    # Проходим по всему списку
    for player_name, task in list(kick_queue.items()):
        # Если время кика пришло
        if task['kick_time'] <= current_time:
            tasks_to_execute.append({
                'player': player_name,
                'reason': task.get('reason', 'Kicked')
            })
            # Удаляем из списка
            del kick_queue[player_name]
    
    if tasks_to_execute:
        return jsonify({
            'status': 'tasks',
            'tasks': tasks_to_execute
        })
    else:
        return jsonify({'status': 'no_tasks'})


# === ЭТОТ АДРЕС БУДЕШЬ ВЫЗЫВАТЬ ТЫ ===
@app.route('/add_kick', methods=['POST'])
def add_kick():
    """Сюда ты отправляешь имя игрока для кика"""
    
    data = request.json
    
    if not data or 'player' not in data:
        return jsonify({'error': 'Укажи имя игрока!'}), 400
    
    player_name = data['player']
    delay_seconds = data.get('delay', 10)  # Через сколько секунд кикнуть
    reason = data.get('reason', 'Нарушение')
    
    # Рассчитываем время кика
    kick_time = datetime.now() + timedelta(seconds=delay_seconds)
    
    # Добавляем в список
    kick_queue[player_name] = {
        'kick_time': kick_time,
        'reason': reason
    }
    
    return jsonify({
        'success': True,
        'message': f'Игрок {player_name} будет кикнут через {delay_seconds} секунд'
    })


# === ПРОВЕРКА, ЧТО СЕРВЕР РАБОТАЕТ ===
@app.route('/')
def home():
    return jsonify({'status': 'Сервер работает!'})


if __name__ == '__main__':
    app.run(port=5000)