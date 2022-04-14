import json
import os
from datetime import datetime
from typing import Dict
import requests


def transform_users(users_d: Dict) -> Dict:
    d = {'report': f"Отчет для {users_d['company']['name']}.",
         'name_email': f"{users_d['name']} <{users_d['email']}> {datetime.now()}"}
    return d


def transform_todos(todos_data: Dict, users_id: int) -> Dict:
    all_tasks = get_count_all_tasks(todos_data, users_id)
    sol_unsol_tasks = find_task_list(todos_data, users_id)
    all_tasks.update(sol_unsol_tasks)
    return all_tasks


def get_count_all_tasks(todos_data: Dict, users_id: int) -> Dict:
    d = {"counter": 0}
    for j in todos_data:
        try:
            if j['userId'] and j['userId'] == users_id and j['title']:
                d["counter"] += 1
            if j['userId'] > users_id:
                break
        except:
            print("Not found userId")
    return d


def find_task_list(todos_data: Dict, users_id: int) -> Dict:
    d = {"counter_t": 0, "counter_f": 0, "completed": '', "not_completed": ''}
    for item in todos_data:
        try:
            if item['userId'] and item['userId'] == users_id and item['title']:
                if item['completed'] == True:
                    d["counter_t"] += 1
                    if len(item['title']) > 48:
                        d["completed"] += item['title'][:48] + '...' + '\n'
                    d["completed"] += item['title'] + '\n'
                else:
                    d["counter_f"] += 1
                    if len(item['title']) > 48:
                        d["not_completed"] += item['title'][:48] + '...' + '\n'
                    d["not_completed"] += item['title'] + '\n'
            if item['userId'] > users_id:
                break
        except:
            print("Not found userId or title")
    print(f"The amount of tasks solved {d['counter_t']}" '\n'
          f"The amount of tasks unsolved {d['counter_f']}")
    return d


def load(merged: Dict, username: str) -> None:
    load_dict = {}
    try:
        if checking_the_file(username) is True:
            print("Xuevi dela")
        else:
            load_dict['first_line'] = f"Отчет для {merged['report']}."
            load_dict['second_line'] = f"{merged['name_email']}"
            load_dict['third_line'] = f"Всего задач: {merged['counter']} \n"
            load_dict['fifth_line'] = f"Завершённые задачи ({merged['counter_t']}): \n{merged['completed']}\n" \
                                      f"Оставшиеся задачи ({merged['counter_f']}): \n{merged['not_completed']}"
            with open(f"tasks/{username}.txt", 'w') as f:
                for line in load_dict:
                    print(f"Writing to file...")
                    f.write(load_dict.get(line) + '\n')
    except:
        print("Error in data transform")


def checking_the_file(file: str) -> bool:
    cur_time = datetime.now()
    if os.path.isfile(f"tasks/{file}.txt"):
        os.rename(f"tasks/{file}.txt", f"tasks/old_{file}_{cur_time.date()}T{cur_time.hour}:"
                                       f"{cur_time.minute}.txt")
        return True
    return False


if __name__ == "__main__":
    users = requests.get('https://json.medrating.org/users')
    users_data = json.loads(users.text)
    todos = requests.get('https://json.medrating.org/todos')
    todo_data = json.loads(todos.text)
    print("Extracted data")

    if not os.path.exists('tasks'):
        os.mkdir('tasks')

    for i in users_data:
        users_transformed_data = transform_users(i)
        todos_transformed_data = transform_todos(todo_data, i['id'])
        print("Data transformation finished")

        merged_res = {**users_transformed_data, **todos_transformed_data}
        print("Merged data")

        load(merged_res, i['username'])
        print("Loaded data")
