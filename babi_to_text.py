from babi_utilities import *

# Data source and output paths
archive_dir = "babi_archive/"
data_dir = "babi_data/text"

# If flag is set will only write utterances and not speaker
utterance_only_flag = False

# Get a list of all the tasks
task_list = os.listdir(archive_dir)
# Remove knowledge base and candidates files
task_list = [file for file in task_list if 'task' in file]

# Get a list of all the dstc2 and babi kb of restaurants
dstc2_kb = load_text_data(archive_dir + "dstc2_kb.txt")
dstc2_kb = set([line.split(' ')[1] for line in dstc2_kb])

babi_kb = load_text_data(archive_dir + "babi_kb.txt")
babi_kb = set([line.split(' ')[1] for line in babi_kb])

for file_name in task_list:

    # Load the file data
    dialogue_file_data = load_text_data(archive_dir + file_name)

    # Process each dialogue
    dialogue_data = process_dialogue(dialogue_file_data, file_name, babi_kb, dstc2_kb)

    # Save to text file
    dialogues_to_text_file(data_dir, dialogue_data['dataset'], dialogue_data['dialogues'], utterance_only_flag)

