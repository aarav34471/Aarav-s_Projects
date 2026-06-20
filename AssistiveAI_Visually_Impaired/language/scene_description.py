#pip install inflect
#pip install language_tool_python
import inflect
p = inflect.engine()
# import language_tool_python
# tool = language_tool_python.LanguageTool('en-US')
import json

test_json_path = 'test_cases.json'

def get_count(object_to_count, inputs):
    counter = 0
    for input in inputs:
        if input == object_to_count:
            counter += 1
    return counter

def in_list(item_to_check, list_to_check):
    for item in list_to_check:
        if (item_to_check['object'] == item['object'] and item_to_check['position'] == item['position']):
            return True
    return False

def unique_counted(input_entities):
    counted_entities = []
    for entity in input_entities:
        if entity['count'] is None:
            if not in_list(entity, counted_entities):
                counted_entity = {
                    "object" : entity['object'],
                    "position" : entity['position'],
                    "count" : get_count(entity, input_entities)
                }
                counted_entities.append(counted_entity)
        else:
            counted_entity = {
                    "object" : entity['object'],
                    "position" : entity['position'],
                    "count" : entity['count']
                }
            counted_entities.append(counted_entity)
    return counted_entities

def construct_sentence(input_entities):
    counted_entities = unique_counted(input_entities)
    sentence = ""
    if len(counted_entities) == 0:
        return "Nothing to see here."
    starter = "There is " if counted_entities[0]['count'] == 1 else "There are "
    for i in range(len(counted_entities)):
        if i == 0:
            sentence += starter
        else:
            sentence += " and "
        entity = counted_entities[i]
        object = entity['object']
        position = entity['position']
        count = entity['count']
        object_snippet = ((p.number_to_words(count) + " " + p.plural_noun(object, count)) if count > 1 else p.a(object)) + " "
        #position_snippet = "" + distance + " " + position
        sentence += object_snippet + position
    sentence += "."
    return sentence

if __name__ == "__main__":
    # test print out sentence
    with open(test_json_path) as f:
        test_cases = json.load(f)

    grammar_counter = 0
    for i in range(len(test_cases)):
        print("========================")
        print(str(i) + ". " + test_cases[i]['description'])
        final_sentence = construct_sentence(test_cases[i]['input'])
        print(final_sentence)
        # matches = tool.check(final_sentence)
        # is_correct = len(matches) == 0
        # print("Grammar check: " + "Correct" if is_correct else "Incorrect")
        # grammar_counter += 1 if is_correct else 0
    # print out percentage correct grammar
    # print("Grammar percentage correct: " + str(grammar_counter / len(test_cases) * 100) + "%")
        
