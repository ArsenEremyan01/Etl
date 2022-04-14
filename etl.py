import json
import os
from datetime import datetime
from typing import Dict
import requests


def extract_users_data() -> Dict:
    """
    Returns the modified json file
    :return: Dict
    """
    try:
        users_dt = requests.get('https://json.medrating.org/users')
        return json.loads(users_dt.text)
    except:
        raise


def extract_todos_data() -> Dict:
    """
    Returns the modified json file
    :return: Dict
    """
    try:
        todos_dt = requests.get('https://json.medrating.org/todos')
        return json.loads(todos_dt.text)
    except:
        raise


def transform_users(user_data: Dict) -> Dict:
    """
    Returns a dictionary with company name, mail, and full name
    :param user_data: dict()
    :return: Dict
    """
    d = {}
    try:
        d['report'] = f"Отчет для {user_data['company']['name']}."
        d['name_email'] = f"{user_data['name']} <{user_data['email']}> {datetime.now()}"
        return d
    except:
        raise


def transform_todos(todos_data: Dict, users_id: int) -> Dict:
    """
    Returns merge of two dictionaries
    :param todos_data: dict()
    :param users_id: int()
    :return: Dict
    """
    try:
        all_tasks = get_count_all_tasks(todos_data, users_id)
        sol_unsol_tasks = find_task_list(todos_data, users_id)
        all_tasks.update(sol_unsol_tasks)
        return all_tasks
    except:
        print("Transformation 'todos_data' failed")


def get_count_all_tasks(todos_data: Dict, users_id: int) -> Dict:
    """
    Returns a dictionary with the number of all tasks
    :param todos_data: dict()
    :param users_id: int()
    :return: Dict
    """
    d = {"counter": 0}
    for j in todos_data:
        try:
            if j['userId'] and j['userId'] == users_id and j['title']:
                d["counter"] += 1
            if j['userId'] > users_id:
                break
            return d
        except:
            print("Not found userId")


def find_task_list(todos_data: Dict, users_id: int) -> Dict:
    """
    Returns a dictionary with the number of (un)solved tasks and list of these tasks
    :param todos_data:
    :param users_id:
    :return: Dict
    """
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


def merge(final_users_data, final_todos_data) -> Dict:
    """
    Returns the merge of the final data
    :param final_users_data: Dict
    :param final_todos_data: Dict
    :return: Dict
    """
    return {**final_users_data, **final_todos_data}


def load(merged: Dict, username: str) -> None:
    """
    The function writes data to file
    :param merged: dict
    :param username: str
    :return: None
    """
    load_dict = {}
    try:
        if check_the_file(f"{username}") is False:
            load_dict['first_line'] = f"Отчет для {merged['report']}."
            load_dict['second_line'] = f"{merged['name_email']}"
            load_dict['third_line'] = f"Всего задач: {merged['counter']} \n"
            load_dict['fifth_line'] = f"Завершённые задачи ({merged['counter_t']}): \n{merged['completed']}\n" \
                                      f"Оставшиеся задачи ({merged['counter_f']}): \n{merged['not_completed']}"

            with open(f"tasks/{username}.txt", 'w') as f:
                print(username)
                for line in load_dict:
                    print(f"Writing to file...")
                    f.write(load_dict.get(line) + '\n')
    except:
        print("Error in data transform")
        raise


def check_the_file(file: str) -> bool:
    """
    Checks if a file exists in directory
    :param file: str
    :return: bool
    """
    cur_time = datetime.now()
    if os.path.exists(f'tasks/{file}.txt'):
        os.rename(f"tasks/{file}.txt", f"tasks/old_{file}_{cur_time.date()}T{cur_time.hour}:"
                                       f"{cur_time.minute}.txt")
        return True

    return False


if __name__ == "__main__":
    users = extract_users_data()
    todos = extract_todos_data()
    print("Extracted data")

    if not os.path.exists('tasks'):
        os.mkdir('tasks')

    for i in users:
        try:
            users_transformed_data = transform_users(i)
            todos_transformed_data = transform_todos(todos, i['id'])
            print("Data transformation finished")

            merged_res = merge(users_transformed_data, todos_transformed_data)
            print("Merged data")

            load(merged_res, i['username'])
            print("Loaded data")
        except:
            raise
