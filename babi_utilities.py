import os
import traceback
import json
import re


def process_dialogue(dialogue_file_data, file_name, babi_kb, dstc2_kb):

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

    for line_index in range(len(dialogue_file_data)):
        line = dialogue_file_data[line_index]

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
                    # Set labels to empty
                    utterance['ap_label'] = ""
                    utterance['da_label'] = ""

                    # Add slots data
                    slots = dict()

                    # Get the next system utterance
                    next_line = dialogue_file_data[line_index + 1].split('\t')
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

    return dialogue_data


def load_json_data(path, file_name):
    try:
        with open(path + file_name + ".json") as file:
            data = json.load(file)

    except (IOError, ValueError):
        traceback.print_exc()
        return False

    return data


def save_json_data(path, file_name, data):
    with open(path + file_name + '.json', 'w+') as file:
        json.dump(data, file, sort_keys=False, indent=4, separators=(',', ': '))


def load_text_data(path, verbose=True):
    with open(path, "r") as file:
        # Read a line and strip newline char
        lines = [line.rstrip('\r\n') for line in file.readlines()]
    if verbose:
        print("Loaded data from file %s." % path)
    return lines


def dialogues_to_text_file(path, file_name, data, utterance_only):
    if utterance_only:
        path = path + "_utt"
    if not os.path.exists(path):
        os.mkdir(path)
    with open(path + "/" + file_name + ".txt", 'w+', encoding="utf8") as file:
        for dialogue in data:
            for utt in dialogue['utterances']:
                if utterance_only:
                    file.write(utt['text'] + "\n")
                else:
                    file.write(utt['speaker'] + "|" + utt['text'] + "\n")
            file.write("\n")
