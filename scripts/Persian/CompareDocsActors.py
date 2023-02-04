from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from doc.models import hugginfaceActors
from doc.models import Actor
from doc.models import DocumentParagraphs

taggingSentenceTokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-base-parsbert-ner-uncased")
taggingSentenceModel = AutoModelForTokenClassification.from_pretrained(
    "HooshvareLab/bert-base-parsbert-ner-uncased")
taggingSentencePipeline = pipeline('ner', model=taggingSentenceModel, tokenizer=taggingSentenceTokenizer)


def apply(folder_name, Country):
    actors = []

    selected_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id=Country.id,
    ).values()

    print("paragraphs selected.......................................")
    print(len(selected_paragraphs))

    selected_actors = Actor.objects.all()
    db_actor_dic = {}
    ahkam_actors_set = set()

    for actor in selected_actors:
        db_actor_dic[actor.id] = actor.forms.split("/")

    print("db actors selected.......................................")

    counter = 1
    for paragraph in selected_paragraphs:
        paragraph_text = paragraph['text']

        output = model_text(paragraph_text)

        if output['result'] == "ERORR":
            print(counter, "...............ERORR")
        else:
            print(counter)
            final_set = combine_json(output)

            for actor in final_set:
                ahkam_actors_set.add((actor, output['text']))

        counter += 1

    print("all docs checked.......................................")

    print("check the actors with db actors.......................................")

    for actor_tuple in ahkam_actors_set:
        is_exist = False
        for actor_form in db_actor_dic.values():
            if actor_tuple[0] in actor_form:
                is_exist = True
                break

        if is_exist:
            continue
        else:
            actors.append(actor_tuple)

    print("delete last info and insert remains into db.......................................")

    hugginfaceActors.objects.filter(country_id=Country.id).delete()
    for actor in actors:
        hugginfaceActors.objects.create(name=actor[0], text=actor[1], country_id=Country.id)


def model_text(text):
    try:
        output = taggingSentencePipeline(text)
        return {"result": output}
    except:
        window_size = 250
        text_parts = text.split(".")
        result = []

        counter = 0

        while counter < len(text_parts):
            my_text = text_parts[counter] + "."
            current_counter = counter

            for j in range(counter + 1, len(text_parts)):
                new_text = text_parts[j]
                if len(my_text.split(" ")) + len(new_text.split(" ")) <= window_size:
                    my_text = my_text + new_text + "."
                else:
                    counter = j - 1
                    break
            else:
                counter = len(text_parts) - 1

            try:
                output = taggingSentencePipeline(my_text)
            except:
                output = "ERROR"
                return {"result": str(output)}

            char_count = 0
            for i in range(current_counter):
                char_count = char_count + len(text_parts[i]) + 1

            for item in output:
                item['start'] += char_count
                item['end'] += char_count

            result.extend(output)

            counter = counter + 1

        return {"result": result, "text": text}


def combine_json(jsonText):
    taggingJson = jsonText['result']
    taggingJson.sort(key=sort_json)
    taggingFinalSet = set()

    for i in range(len(taggingJson)):
        item_object = taggingJson[i]

        # TODO: mistake
        if item_object['entity'][0] == "I":
            continue

        if item_object['entity'].split("-")[1] != "organization":
            continue

        end_word_index = item_object['end']
        word = item_object['word']

        for j in range(i + 1, len(taggingJson)):
            iObject = taggingJson[j]

            if iObject['entity'][0] == "B":
                break

            if iObject['entity'].split("-")[1] != "organization":
                break

            if end_word_index + 10 < iObject['start']:
                taggingJson[i]['entity'] = taggingJson[i]['entity'].replace("I", "B")
                break

            end_word_index = iObject['end']
            word = word + " " + iObject['word']

        taggingFinalSet.add(word)

    return taggingFinalSet


def sort_json(item):
    return item['start']
