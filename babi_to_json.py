import os
import re
from babi_utilities import *

# Data source and output paths
archive_dir = "babi_archive/"
data_dir = "babi_data/"

# Get a list of all the tasks
task_list = os.listdir(archive_dir)
# Remove knowledge base and candidates files
task_list = [file for file in task_list if 'task' in file]

for file_name in task_list:

    # Load the file data
    file_data = load_data(archive_dir + file_name)

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

            # Check this line is not an api call option
            if any(char in ['_'] for char in text[0]):
                continue

            # Remove the numbers and '<SILENCE>' from beginning of user utterances
            user_utt = text[0].split(' ')
            if re.match("\d", user_utt[0]):
                del user_utt[0]
            if user_utt[0] == '<SILENCE>':
                del user_utt[0]

            # Join into complete sentence
            user_utt = ' '.join(user_utt)
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

            sys_utt = text[1].split(' ')
            # If it is an api call then make slots instead
            if sys_utt[0] != 'api_call':

                # Join into complete sentence
                sys_utt = ' '.join(sys_utt)

                utterance = dict()
                # Set speaker
                utterance['speaker'] = "SYS"
                # Set the utterance text
                utterance['text'] = sys_utt
                # Set labels to empty
                utterance['ap_label'] = ""
                utterance['da_label'] = ""

                # Add slots data
                slots = dict()

                # Get the next system utterance
                next_line = file_data[line_index + 1].split('\t')
                if len(next_line) > 1:
                    next_sys_utt = next_line[1].split(' ')

                    # If it contains an api call, convert to slots
                    if next_sys_utt[0] == 'api_call':

                        # If it is the dstc task, there are only 3 slots
                        if file_name.split('_')[0] == 'task6':
                            slots['food_type'] = next_sys_utt[1]
                            slots['location'] = next_sys_utt[2]
                            slots['price'] = next_sys_utt[3]
                        # Else there are 4 slots
                        else:
                            slots['food_type'] = next_sys_utt[1]
                            slots['location'] = next_sys_utt[2]
                            slots['num_guests'] = next_sys_utt[3]
                            slots['price'] = next_sys_utt[4]

                utterance['slots'] = slots

                # Add to utterances
                num_utterances += 1
                utterances.append(utterance)

        # Else we have finished a dialogue so create the object
        else:
            # Create dialogue
            dialogue['dialogue_id'] = dataset_name + '_' + str(num_dialogues + 1)
            dialogue['num_utterances'] = num_utterances
            dialogue['utterances'] = utterances

            # Create the scenario
            scenario = dict()
            scenario['db_id'] = dataset_name + '_' + str(num_dialogues + 1)
            scenario['db_type'] = 'restaurant booking'
            scenario['task'] = 'restaurant booking'
            scenario['items'] = []
            dialogue['scenario'] = scenario

            # Add to dialogues
            num_dialogues += 1
            dialogues.append(dialogue)

            dialogue = dict()
            utterances = []
            num_utterances = 0

    # Add dataset metadata
    dialogue_data['dataset'] = "babi_" + file_name
    dialogue_data['num_dialogues'] = num_dialogues
    dialogue_data['dialogues'] = dialogues

    # Save to JSON file
    save_json_data(data_dir, dialogue_data['dataset'], dialogue_data)