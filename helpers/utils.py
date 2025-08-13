import os, logging, json, random, logging


def setup_logging(log_file):
    """
    Setup logging configuration
    """
    # Create the folder (and subfolders if necessary) if they do not exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_random_user_agent(file_path='resources/user_agent.json'):
    """
    Get a random user agent from a JSON file.
    """
    default_user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    try:
        with open(file_path, 'r') as file:
            user_agents = json.load(file)
            if not user_agents:
                logging.warning(f"The user agent file '{file_path}' is empty. Using default user agent.")
                return default_user_agent
            user_agent = random.choice(user_agents)
            return user_agent['useragent'] if 'useragent' in user_agent else default_user_agent
    except FileNotFoundError:
        logging.error(f"The file {file_path} not found.")
        return default_user_agent
    except json.JSONDecodeError:
        logging.error(f"The file {file_path} is not a valid JSON file.")
        print(3)
        return default_user_agent

def format_number(num):
    """
    Format a number into a human-readable string.
    """
    try:
        if num >= 10**9:
            return f"{num / 10**9:.2f}B"
        elif num >= 10**6:
            return f"{num / 10**6:.2f}M"
        elif num >= 10**3:
            return f"{num / 10**3:.2f}K"
        else:
            return str(num)
    except Exception as e:
        logging.error(f"Error formatting number:\n >> {e}")
        return "O"
