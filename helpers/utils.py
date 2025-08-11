import os, logging


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
