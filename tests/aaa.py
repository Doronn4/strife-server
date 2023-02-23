string = """
        'file_in_chat': 1,
        'profile_pic_change': 2
"""

lines = string.replace('\n', '').split(',')

for line in lines:
    parts = line.split(':')
    print(f'{parts[1]}: {parts[0]},')