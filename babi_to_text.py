import os
import re
from babi_utilities import *

# Data source and output paths
archive_dir = "babi_archive/"
data_dir = "babi_data/text/"

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
    file_data = load_text_data(archive_dir + file_name)

    # Split the file name into task number and dataset
    file_name = file_name.split('.')[0]
    file_name = file_name.replace("dev", "eval")
    dataset_name = file_name.split('_')[0] + '_' + file_name.split('_')[-1]

    dialogue_data = dict()
    dialogues = []
    num_dialogues = 0

    dialogue = dict()
    utterances = []
    num_utterances = 0

    for line_index in range(len(file_data)):
        line = file_data[line_index]

        # For each turn in the dialogue (dialogues are split on empty lines)
        if line is not '':

            # Split on tabs to separate user and system utterances
            text = line.split('\t')

            # Remove the numbers and '<SILENCE>' from beginning of user utterances
            user_utt = text[0].split(' ')
            if re.match("\d", user_utt[0]):
                del user_utt[0]
            if user_utt[0] == '<SILENCE>':
                del user_utt[0]

            # Check this line is not an api call option
            if file_name.split('_')[0] == 'task6':
                if any(word in dstc2_kb for word in user_utt) or (len(user_utt) > 1 and user_utt[0] == 'api_call'):
                    user_utt = []
            elif len(user_utt) > 1 and user_utt[0] in babi_kb:
                user_utt = []

            # If it contains a return value for an api call surround with angle brackets
            for i in range(len(user_utt)):
                if any(char in ['_'] for char in user_utt[i]):
                    user_utt[i] = '<' + user_utt[i] + '>'

            # Join into complete sentence
            user_utt = ' '.join(user_utt)
            user_utt.strip()
            if user_utt is not '':

                utterance = dict()
                # Set speaker
                utterance['speaker'] = "USR"
                # Set the utterance text
                utterance['text'] = user_utt
                # Set labels to empty
                utterance['ap_label'] = ""
                utterance['da_label'] = ""
                # Add empty slots data
                utterance['slots'] = dict()

                # Add to utterances
                num_utterances += 1
                utterances.append(utterance)

            # Get the system utterance
            if len(text) > 1:
                sys_utt = text[1].split(' ')
            else:
                sys_utt = None
            # If it is not an api call then make utterance
            if sys_utt and sys_utt[0] != 'api_call':

                # If it contains a return value for an api call surround with angle brackets
                for i in range(len(sys_utt)):
                    if any(char in ['_'] for char in sys_utt[i]) or sys_utt[i] in dstc2_kb:
                        sys_utt[i] = '<' + sys_utt[i] + '>'

                # Join into complete sentence
                sys_utt = ' '.join(sys_utt)
                sys_utt.strip()
                if sys_utt is not '':

                    utterance = dict()
                    # Set speaker
                    utterance['speaker'] = "SYS"
                    # Set the utterance text
                    utterance['text'] = sys_utt

                    # Add to utterances
                    num_utterances += 1
                    utterances.append(utterance)

        # Else we have finished a dialogue so create the object
        else:
            # Create dialogue
            dialogue['dialogue_id'] = dataset_name + '_' + str(num_dialogues + 1)
            dialogue['num_utterances'] = num_utterances
            dialogue['utterances'] = utterances

            # Add to dialogues
            dialogues.append(dialogue)
            num_dialogues += 1

            dialogue = dict()
            utterances = []
            num_utterances = 0

    file_name = "babi_" + file_name
    # Write to text file
    with open(data_dir + file_name + '.txt', 'w+', encoding="utf8") as file:
        for dialogue in dialogues:
            for utt in dialogue['utterances']:
                file.write(utt['speaker'] + "|" + utt['text'] + "\n")
            file.write("\n")
