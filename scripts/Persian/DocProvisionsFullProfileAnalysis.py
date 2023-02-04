import json

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, MT5Tokenizer, \
    MT5ForConditionalGeneration, AutoModelForSequenceClassification
from doc.models import FullProfileAnalysis
from doc.models import DocumentParagraphs
import after_response

taggingSentenceTokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-base-parsbert-ner-uncased")
taggingSentenceModel = AutoModelForTokenClassification.from_pretrained(
    "HooshvareLab/bert-base-parsbert-ner-uncased")
taggingSentencePipeline = pipeline('ner', model=taggingSentenceModel, tokenizer=taggingSentenceTokenizer)

sentimentAnalyserTokenizer = MT5Tokenizer.from_pretrained("persiannlp/mt5-base-parsinlu-sentiment-analysis")
sentimentAnalyserModel = MT5ForConditionalGeneration.from_pretrained("persiannlp/mt5-base-parsinlu-sentiment-analysis")

classificationSentenceTokenizer = AutoTokenizer.from_pretrained("m3hrdadfi/albert-fa-base-v2-clf-persiannews")
classificationSentenceModel = AutoModelForSequenceClassification.from_pretrained(
    "m3hrdadfi/albert-fa-base-v2-clf-persiannews")
classificationSentencePipeline = pipeline('text-classification', model=classificationSentenceModel,
                                          tokenizer=classificationSentenceTokenizer, top_k=None)


@after_response.enable
def apply(folder_name, Country):
    # file = open("result.txt", "r", encoding="utf-8")
    # delimiter = "&!&"
    # text = file.read()
    # items = text.split("\n")
    # counter = 1
    # FullProfileAnalysis.objects.filter(country_id=Country.id).delete()
    # for item in items:
    #     itemArray = item.split(delimiter)
    #     pId = itemArray[0]
    #     if pId:
    #         pTagRes = itemArray[3].replace("'", "\"")
    #         pClassification = itemArray[1]
    #         pSentiment = itemArray[2]
    #         try:
    #             taggingResult = json.loads(pTagRes)
    #             organizations = taggingResult['organizations']
    #             locations = taggingResult['locations']
    #             persons = taggingResult['persons']
    #             FullProfileAnalysis.objects.create(country_id=Country.id, document_paragraph_id=int(pId),
    #                                                sentiment=pSentiment, classification_subject=pClassification,
    #                                                persons=persons, locations=locations, organizations=organizations)
    #             if counter % 500 == 0:
    #                 print(counter, pId)
    #         except Exception as inst:
    #             print("................ERROR...................", counter, pId, inst)
    #
    #         counter += 1
    # file.close()

    analysis = []
    print('paragraphs is going to select')
    selected_paragraphs = DocumentParagraphs.objects.filter(
        document_id__country_id__id=Country.id).values()
    print('paragraphs selected', len(selected_paragraphs))

    print('start processing......................................')

    error_count = 0
    counter = 0
    for paragraph in selected_paragraphs:
        counter += 1
        if len(paragraph['text']) < 80:
            error_count += 1
            print(counter, '...less than 80 character...')
            continue

        try:
            classification_model_result = text_classifications_analysis(paragraph['text'])
            tagging_model_result = text_tagging_analysis(paragraph['text'])
            sentiment_model_result = text_sentiment_analysis(paragraph['text'])
            classification_result = process_text_classification_model(classification_model_result['result'])
            tagging_result = process_text_tagging_model(tagging_model_result['result'], paragraph['text'])
            sentiment_result = process_text_sentiment_model(sentiment_model_result['result'][0])

            analysis.append((paragraph['id'], sentiment_result, classification_result, tagging_result))

        except Exception as e:
            print("....................................................")
            print(counter)
            print(".......ERROR: ", "paragraphID: ", paragraph['id'])
            print(e)
            print("....................................................")

        print(counter)

    print('processing completed --- ', 'less than 80 characters:', error_count)

    print("write result in result.txt")
    file = open("result.txt", "w", encoding="utf-8")
    delimiter = "&!&"
    for item in analysis:
        result_text = delimiter.join([str(value) for value in item])
        file.write(result_text + "\n")
    file.close()

    print('insert in database')
    FullProfileAnalysis.objects.filter(country_id=Country.id).delete()

    for item in analysis:
        FullProfileAnalysis.objects.create(country=Country, sentiment=item[1],
                                           classification_subject=item[2], persons=item[3]['persons'],
                                           locations=item[3]['locations'], organizations=item[3]['organizations'],
                                           document_paragraph_id=item[0])

    Country.status = "Done"
    Country.save()
    print('finished successfully')


def text_sentiment_analysis(text):
    input_ids = sentimentAnalyserTokenizer.encode(text, return_tensors="pt")
    res = sentimentAnalyserModel.generate(input_ids)
    output = sentimentAnalyserTokenizer.batch_decode(res, skip_special_tokens=True)
    return {"result": output}


def text_classifications_analysis(text):
    try:
        output = classificationSentencePipeline(text)
        return {"result": output}
    except:
        window_size = 250
        text_parts = text.split(".")
        result = []

        counter = 0

        while counter < len(text_parts):
            my_text = text_parts[counter] + "."

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
                output = classificationSentencePipeline(my_text)
            except:
                output = "ERROR"
                return {"result": output}

            result.extend(output)

            counter = counter + 1

        final_result = []
        for i in range(8):
            label = result[0][i]['label']
            score = 0

            for j in range(len(result)):
                array = result[j]

                for obj in array:
                    if obj['label'] == label:
                        score += obj['score']
                        break

            final_result.append({'label': label, 'score': score / len(result)})

        return {"result": result}


def text_tagging_analysis(text):
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
                return {"result": output}

            char_count = 0
            for i in range(current_counter):
                char_count = char_count + len(text_parts[i]) + 1

            for item in output:
                item['start'] += char_count
                item['end'] += char_count

            result.extend(output)

            counter = counter + 1

        return {"result": result, "text": text}


def process_text_sentiment_model(sentiment_model_result):
    if sentiment_model_result == "mixed" or sentiment_model_result == "neutral":
        return "احساس خنثی یا ترکیبی از مثبت و منفی"
    elif sentiment_model_result == "borderline":
        return "احساس خنثی یا ترکیبی از مثبت و منفی"
    elif sentiment_model_result == "no sentiment expressed":
        return "بدون ابراز احساسات"
    elif sentiment_model_result == "very positive":
        return 'احساس بسیار مثبت'
    elif sentiment_model_result == "positive":
        return 'احساس مثبت'
    elif sentiment_model_result == "very negative":
        return 'احساس بسیار منفی'
    elif sentiment_model_result == "negative":
        return 'احساس منفی'
    else:
        return '----'


def process_text_classification_model(classification_model_result):
    classification_array = classification_model_result[0]

    max_score = 0
    max_label = ''
    for item in classification_array:
        if item['score'] > max_score:
            max_score = item['score']
            max_label = item['label']

    return max_label


def process_text_tagging_model(tagging_model_result, paragraph_text):
    taggingJson = tagging_model_result
    taggingJson.sort(key=sort_json)

    taggingPersonArray = []
    taggingLocationArray = []
    taggingOrganizationArray = []
    taggingDateArray = []
    taggingMoneyArray = []
    taggingTimeArray = []
    taggingPercentArray = []
    taggingFacilityArray = []
    taggingProductArray = []
    taggingEventArray = []

    for i in range(len(taggingJson)):
        item_object = taggingJson[i]

        item_object_start = item_object['entity'].split("-")[0]
        item_object_end = item_object['entity'].split("-")[1]
        if item_object_start == "I":
            continue

        if item_object_end not in ["person", "location", "organization", "date", "time", "money", "percent", "facility",
                                   "product", "event"]:
            continue

        end_word_index = item_object['end']
        start_word_index = item_object['start']

        for j in range(i + 1, len(taggingJson)):
            iObject = taggingJson[j]

            if iObject['entity'][0] == "B":
                break

            iObject_entity = iObject['entity'].split("-")[1]
            if iObject_entity != item_object_end:
                taggingJson[j]['entity'] = taggingJson[j]['entity'].replace("I", "B")
                break

            if end_word_index + 10 < iObject['start']:
                taggingJson[j]['entity'] = taggingJson[j]['entity'].replace("I", "B")
                break

            end_word_index = iObject['end']

        word = paragraph_text[start_word_index:end_word_index]
        item_object_entity = item_object['entity'].split("-")[1]
        if item_object_entity == "person":
            taggingPersonArray.append(word)
        elif item_object_entity == "location":
            taggingLocationArray.append(word)
        elif item_object_entity == "organization":
            taggingOrganizationArray.append(word)
        elif item_object_entity == "date":
            taggingDateArray.append(word)
        elif item_object_entity == "time":
            taggingTimeArray.append(word)
        elif item_object_entity == "money":
            taggingMoneyArray.append(word)
        elif item_object_entity == "percent":
            taggingPercentArray.append(word)
        elif item_object_entity == "facility":
            taggingFacilityArray.append(word)
        elif item_object_entity == "product":
            taggingProductArray.append(word)
        elif item_object_entity == "event":
            taggingEventArray.append(word)

    return {'persons': ';'.join(taggingPersonArray), 'locations': ';'.join(taggingLocationArray),
            'organizations': ';'.join(taggingOrganizationArray), 'dates': ';'.join(taggingDateArray),
            'times': ';'.join(taggingTimeArray), 'moneys': ';'.join(taggingMoneyArray),
            'percents': ';'.join(taggingPercentArray), 'facilities': ';'.join(taggingFacilityArray),
            'product': ';'.join(taggingProductArray), 'events': ';'.join(taggingEventArray)}


def sort_json(item):
    return item['start']
