import logging


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def format_number(num):
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
        print(f"Error formatting number: {e}")
        return "O"
