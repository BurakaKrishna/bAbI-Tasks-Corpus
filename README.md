# bAbl-Corpus
Utilities for processing the 6 dialogue bAbI Tasks available from [facebook research](https://research.fb.com/downloads/babi/).
The set of 6 tasks are designed to test end-to-end dialogue systems in the restaurant domain described in the paper
[Learning End-to-End Goal-Oriented Dialog](https://research.fb.com/publications/learning-end-to-end-goal-oriented-dialog/).
Each task tests a unique aspect of dialogue and the original 1000 dialogues for training,
1000 for development and 1000 for testing have been preserved.
Tasks 1-5 also include a second test set (with suffix OOV) that contains dialogues with entities not present in training and development sets.

## Scripts
babi_to_json.py script processes the dialogues from the original text format into .json files using the format
outlined below.
This format is intended to facilitate annotation of the dialogue using the 
[Conversation Analysis Schema](https://nathanduran.github.io/CA-Schema/)
and [Dialogue tagger](https://github.com/NathanDuran/CA-Dialogue-Tagger).

babi_to_text.py processes the dialogues from the original text format into plain text files,
with one line per-utterance, using the format outlined below.
Setting the *utterance_only* flag to true will remove the speaker label from the output text files.

babi_utilities.py script contains various helper functions for loading/saving and processing the data.

## Data Format
The original dialogues (in tasks 3, 4, 5 and 6) have had all lines relating to API calls that do not include dialogue removed,
for example, *'resto_rome_moderate_italian_3stars'*.

System API calls within utterances (in tasks 1, 2 and 5), for example, *'api_call french paris four expensive'* 
have been converted into slot values within the json files or discarded in the plain text files.

Return or search values for API calls (in tasks 3, 4, 5 and 6) have been surrounded by angle brackets to differentiate them from normal text,
for example, *\<gourmet_burger_kitchen\>*

All instances of *\<SILENCE\>*  and line numbers have been removed.

The *USR* and *SYS* speaker labels have been added to each utterance.

### Example Text Format
Individual dialogues in a set are separated with an empty line.

USR|good morning

SYS|hello what can i help you with today

USR|can you book a table

SYS|i'm on it

### Example JSON Format
The following is an example of the JSON format for the bAbI corpus.

```json
    {
        "dataset": "dataset_name",
        "num_dialogues": 1,
        "dialogues": [
            {
                "dialogue_id": "dataset_name_1",
                "num_utterances": 2,
                "utterances": [
                    {
                        "speaker": "A",
                        "text": "Utterance 1 text.",
                        "ap_label": "AP-Label",
                        "da_label": "DA-Label"
                    },
                    {
                        "speaker": "B",
                        "text": "Utterance 2 text.",
                        "ap_label": "AP-Label",
                        "da_label": "DA-Label",
                        "slots": { //Optional
                            "slot_name": "slot_value"
                        }
                    }
                ],
                "scenario": { //Optional
                    "db_id": "1",
                    "db_type": "i.e booking",
                    "task": "i.e book",
                    "items": []
                }
            }
        ]
    }
```
