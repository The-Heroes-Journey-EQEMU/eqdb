import os

def get_exclusion_list(category):
    """
    Reads a list of item IDs from a text file in the Exclusion folder.
    """
    exclusion_list = []
    # Construct the full path to the file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'Exclusion', f'{category}.txt')

    if not os.path.exists(file_path):
        return exclusion_list

    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    exclusion_list.append(line.strip())
                except ValueError:
                    # Handle cases where a line is not a valid integer
                    pass
    return exclusion_list
