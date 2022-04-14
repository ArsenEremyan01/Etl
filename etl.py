import json
import os
from datetime import datetime
from typing import Dict
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def extract_users_data() -> Dict:
    """
    Extracts users data
    :return: Dict
    """
    users_dt = requests.get('https://json.medrating.org/users')
    return json.loads(users_dt.text)


def extract_todos_data() -> Dict:
    """
    Extracts TODOS data
    :return: Dict
    """
    todos_dt = requests.get('https://json.medrating.org/todos')
    return json.loads(todos_dt.text)


def transform_users(user_data: Dict) -> Dict:
    """
    Transforms users data to relevant
    :param user_data: dict()
    :return: Returns a dictionary with company name, mail, and full name
    """
    d = {}
    d['report'] = f"Отчет для {user_data['company']['name']}."
    d['name_email'] = f"{user_data['name']} <{user_data['email']}> {datetime.now()}"
    return d


def transform_todos(todos_data: Dict, users_id: int) -> Dict:
    """
    Transforms todos data to relevant format
    :param todos_data: dict()
    :param users_id: int()
    :return: Returns merge of two dictionaries
    """
    all_tasks = get_count_all_tasks(todos_data, users_id)
    sol_unsol_tasks = find_task_list(todos_data, users_id)
    all_tasks.update(sol_unsol_tasks)
    return all_tasks


def get_count_all_tasks(todos_data: Dict, users_id: int) -> Dict:
    """
    Counts number of tasks for specific user
    :param todos_data: dict()
    :param users_id: int()
    :return: a dictionary with the number of all tasks
    """
    d = {"counter": 0}
    for j in todos_data:
        if j['userId'] and j['userId'] == users_id and j['title']:
            d["counter"] += 1
        if j['userId'] > users_id:
            break
        return d


def find_task_list(todos_data: Dict, users_id: int) -> Dict:
    """
    Method counts number of (un)solved tasks
    Returns
    :param todos_data:
    :param users_id:
    :return: a dictionary with the number of (un)solved tasks
    """
    d = {"counter_t": 0, "counter_f": 0, "completed": '', "not_completed": ''}
    for item in todos_data:
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
    return d


def merge(final_users_data, final_todos_data) -> Dict:
    """
    Method combines user and todos datasets
    :param final_users_data: Dict
    :param final_todos_data: Dict
    :return: the merge of the final data
    """
    return {**final_users_data, **final_todos_data}


def load(merged: Dict, username: str) -> None:
    """
    The function loads data into file
    :param merged: combined users and todos dataset
    :param username: username
    :return: None
    """
    load_dict = {}
    if check_the_file(f"{username}") is False:
        load_dict['first_line'] = f"Отчет для {merged['report']}."
        load_dict['second_line'] = f"{merged['name_email']}"
        load_dict['third_line'] = f"Всего задач: {merged['counter']} \n"
        load_dict['fifth_line'] = f"Завершённые задачи ({merged['counter_t']}): \n{merged['completed']}\n" \
                                  f"Оставшиеся задачи ({merged['counter_f']}): \n{merged['not_completed']}"

        with open(f"tasks/{username}.txt", 'w') as f:
            logging.info('Username: ' + username)
            logging.info("Writing to file...")
            for line in load_dict:
                f.write(load_dict.get(line) + '\n')


def check_the_file(file: str) -> bool:
    """
    Checks if a file exists in directory
    :param file: str
    :return: bool
    """
    cur_time = datetime.now()
    fpath = f'tasks/{file}.txt'
    if os.path.exists(fpath):
        os.rename(fpath, f"tasks/old_{file}_{cur_time.date()}T{cur_time.hour}:{cur_time.minute}.txt")
        return True
    return False


def init_folders():
    """
    Method creates required folders
    """
    if not os.path.exists('tasks'):
        os.mkdir('tasks')


if __name__ == "__main__":

    init_folders()
    users = []
    todos = []
    try:
        logging.info("Extracting datasets via API")
        users = extract_users_data()
        todos = extract_todos_data()
    except Exception as e:
        logging.error("Error extracting users data. Message: " + str(e))
        exit()

    for idx, i in enumerate(users):
        try:
            logging.info(f"Task number: {idx + 1}")

            users_transformed_data = transform_users(i)
            todos_transformed_data = transform_todos(todos, i['id'])
            logging.info("Data transformation finished")

            merged_res = merge(users_transformed_data, todos_transformed_data)
            logging.info("Merged data")

            load(merged_res, i['username'])
            logging.info(f"Loaded data \n")
        except Exception as e:
            logging.error(f"Error processing user data. Message: {str(e)} \n Input Data: {i}")
