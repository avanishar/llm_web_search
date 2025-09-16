import os

def combine_logs(log_folder):
    """
    Combines all log files in a folder into one string.
    """
    combined_content = ""
    for file in sorted(os.listdir(log_folder)):
        if file.endswith(".md"):
            with open(os.path.join(log_folder, file), "r", encoding="utf-8") as f:
                combined_content += f.read() + "\n\n"
    return combined_content
