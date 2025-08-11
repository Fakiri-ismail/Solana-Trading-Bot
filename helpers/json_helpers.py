import os, json, logging


def read_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    return []


def write_json_file(file_path, data):
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def add_json_record(file_path: str, record) -> None:
    data = read_json_file(file_path)
    
    if type(record) is list:
        data = data + record
    else:
        data.append(record)

    write_json_file(file_path, data)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info("File deleted.")
    else:
        logging.warning(f"File '{file_path}'not found.")
