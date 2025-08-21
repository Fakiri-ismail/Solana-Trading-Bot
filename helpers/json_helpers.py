import os, json, logging


def read_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
            if content.strip():
                return json.loads(content)
            logging.warning(f"File '{file_path}' is empty.")
    else:
        logging.warning(f"File '{file_path}' not found.")


def write_json_file(file_path, data):
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def update_json_record(file_path: str, key: str, value) -> bool:
    data = read_json_file(file_path)
    if data:
        data[key] = value
        write_json_file(file_path, data)
        return True
    return False


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info("File deleted.")
    else:
        logging.warning(f"File '{file_path}'not found.")
