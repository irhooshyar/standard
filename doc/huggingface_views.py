
from django.http import JsonResponse, HttpResponse
from transformers import MT5ForConditionalGeneration, MT5Tokenizer, AutoTokenizer, AutoModelForTokenClassification, \
    pipeline, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM

# ---------- Huggingface configs ---------------
from abdal.config import HUGGINGFACE_CONFIGS

auto_translator_model_name = None
auto_translator_tokenizer = None
auto_translator_model = None

taggingSentenceTokenizer =None
taggingSentenceModel = None
taggingSentencePipeline = None

classificationSentenceTokenizer =None
classificationSentenceModel = None
classificationSentencePipeline = None

sentimentAnalyserTokenizer = None
sentimentAnalyserModel = None

summary_tokenizer = None
summary_model = None
# --------------------------------------------------------


if HUGGINGFACE_CONFIGS['machineTranslator'] == "global":
    auto_translator_model_name = "persiannlp/mt5-base-parsinlu-opus-translation_fa_en"
    auto_translator_tokenizer = MT5Tokenizer.from_pretrained(auto_translator_model_name)
    auto_translator_model = MT5ForConditionalGeneration.from_pretrained(auto_translator_model_name)

if HUGGINGFACE_CONFIGS['sentimentAnalyser'] == "global":
    sentimentAnalyserTokenizer = MT5Tokenizer.from_pretrained("persiannlp/mt5-base-parsinlu-sentiment-analysis")
    sentimentAnalyserModel = MT5ForConditionalGeneration.from_pretrained(
        "persiannlp/mt5-base-parsinlu-sentiment-analysis")

if HUGGINGFACE_CONFIGS['taggingAnalyser'] == "global":
    taggingSentenceTokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-base-parsbert-ner-uncased")
    taggingSentenceModel = AutoModelForTokenClassification.from_pretrained(
        "HooshvareLab/bert-base-parsbert-ner-uncased")
    taggingSentencePipeline = pipeline('ner', model=taggingSentenceModel, tokenizer=taggingSentenceTokenizer)

if HUGGINGFACE_CONFIGS['classificationAnalyser'] == "global":
    classificationSentenceTokenizer = AutoTokenizer.from_pretrained("m3hrdadfi/albert-fa-base-v2-clf-persiannews")
    classificationSentenceModel = AutoModelForSequenceClassification.from_pretrained(
        "m3hrdadfi/albert-fa-base-v2-clf-persiannews")
    classificationSentencePipeline = pipeline('text-classification', model=classificationSentenceModel,
                                            tokenizer=classificationSentenceTokenizer, top_k=None)

if HUGGINGFACE_CONFIGS['summarizer'] == "global":
    summary_tokenizer = AutoTokenizer.from_pretrained("alireza7/ARMAN-SH-persian-base-perkey-summary")
    summary_model = AutoModelForSeq2SeqLM.from_pretrained("alireza7/ARMAN-SH-persian-base-perkey-summary")



def auto_translator(request, text, **generator_args):
    local_auto_translator_model_name = auto_translator_model_name
    local_auto_translator_tokenizer = auto_translator_tokenizer
    local_auto_translator_model = auto_translator_model
    
    if HUGGINGFACE_CONFIGS['machineTranslator'] == "local":
        local_auto_translator_model_name = "persiannlp/mt5-base-parsinlu-opus-translation_fa_en"
        local_auto_translator_tokenizer = MT5Tokenizer.from_pretrained(local_auto_translator_model_name)
        local_auto_translator_model = MT5ForConditionalGeneration.from_pretrained(local_auto_translator_model_name)
    
    try:
        input_ids = local_auto_translator_tokenizer.encode(text, return_tensors="pt")
        res = local_auto_translator_model.generate(input_ids, **generator_args)
        output = local_auto_translator_tokenizer.batch_decode(res, skip_special_tokens=True)
        output = list(output)[0].replace(".", "").lower()
    except:
        output = "ERROR"
    return JsonResponse({'result': output})


def sentiment_analyser(request, text, **generator_args):
    local_sentimentAnalyserTokenizer = sentimentAnalyserTokenizer
    local_sentimentAnalyserModel = sentimentAnalyserModel

    if HUGGINGFACE_CONFIGS['sentimentAnalyser'] == "local":
        local_sentimentAnalyserTokenizer = MT5Tokenizer.from_pretrained("persiannlp/mt5-base-parsinlu-sentiment-analysis")
        local_sentimentAnalyserModel = MT5ForConditionalGeneration.from_pretrained(
            "persiannlp/mt5-base-parsinlu-sentiment-analysis")

    input_ids = local_sentimentAnalyserTokenizer.encode(text, return_tensors="pt")
    res = local_sentimentAnalyserModel.generate(input_ids, **generator_args)
    output = local_sentimentAnalyserTokenizer.batch_decode(res, skip_special_tokens=True)
    return JsonResponse({"result": output})


def tagging_analyser(request, text):
    local_taggingSentenceTokenizer = taggingSentenceTokenizer
    local_taggingSentenceModel = taggingSentenceModel
    local_taggingSentencePipeline =  taggingSentencePipeline

    if HUGGINGFACE_CONFIGS['taggingAnalyser'] == "local":
        local_taggingSentenceTokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-base-parsbert-ner-uncased")
        local_taggingSentenceModel = AutoModelForTokenClassification.from_pretrained(
            "HooshvareLab/bert-base-parsbert-ner-uncased")
        local_taggingSentencePipeline = pipeline('ner', model=local_taggingSentenceModel, tokenizer=local_taggingSentenceTokenizer)

    try:
        output = local_taggingSentencePipeline(text)
        return JsonResponse({"result": str(output)})
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
                return JsonResponse({"result": str(output)})

            char_count = 0
            for i in range(current_counter):
                char_count = char_count + len(text_parts[i]) + 1

            for item in output:
                item['start'] += char_count
                item['end'] += char_count

            result.extend(output)

            counter = counter + 1

        return JsonResponse({"result": str(result)})



def classification_analyser(request, text):
    local_classificationSentenceTokenizer = classificationSentenceTokenizer
    local_classificationSentenceModel = classificationSentenceModel
    local_classificationSentencePipeline = classificationSentencePipeline

    if HUGGINGFACE_CONFIGS['classificationAnalyser'] == "local":
        local_classificationSentenceTokenizer = AutoTokenizer.from_pretrained("m3hrdadfi/albert-fa-base-v2-clf-persiannews")
        local_classificationSentenceModel = AutoModelForSequenceClassification.from_pretrained(
            "m3hrdadfi/albert-fa-base-v2-clf-persiannews")
        local_classificationSentencePipeline = pipeline('text-classification', model=local_classificationSentenceModel,
                                                tokenizer=local_classificationSentenceTokenizer, top_k=None)

    try:
        output = local_classificationSentencePipeline(text)
        return JsonResponse({"result": str(output)})
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
                output = classificationSentencePipeline(my_text)
            except:
                output = "ERROR"
                return JsonResponse({"result": output})

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

        return JsonResponse({"result": str(result)})


def GetTextSummary(request):
    local_summary_tokenizer = summary_tokenizer
    local_summary_model = summary_model

    if HUGGINGFACE_CONFIGS['summarizer'] == "local":
        print('local-summary')
        local_summary_tokenizer = AutoTokenizer.from_pretrained("alireza7/ARMAN-SH-persian-base-perkey-summary")
        local_summary_model = AutoModelForSeq2SeqLM.from_pretrained("alireza7/ARMAN-SH-persian-base-perkey-summary")


    input_text = request.POST.get('text')
    
    try:
        tokens = local_summary_tokenizer(input_text, return_tensors="pt")
        generated_tokens = local_summary_model.generate(tokens['input_ids'])
        result = " ".join(local_summary_tokenizer.convert_ids_to_tokens(generated_tokens[0], skip_special_tokens=True)).replace(
            "▁", "").replace("< n >", "").replace("n >", "")
    except:
        result = "متن وارد شده طولانی است."
    print(f'result= {result}')
    return JsonResponse({"text_summary": result})
