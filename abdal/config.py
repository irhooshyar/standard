import os
from pathlib import Path

BASE_PATH = Path(os.path.dirname(__file__)).parent
MEDIA_PATH = Path(BASE_PATH, 'media_cdn')
DATA_PATH = Path(BASE_PATH, 'media_cdn', "data")

DECISION_TREE_PATH = Path(BASE_PATH, 'media_cdn', "decision_tree_data")
DOC_STATIC_PATH = Path(BASE_PATH, 'doc','static')
DENDROGRAM_PATH = Path(DOC_STATIC_PATH, "dendrogram_plots")

#/****** Advanced ARIMA ******/ 
ACF_PATH = Path(DOC_STATIC_PATH, "ACF_plot")
PACF_PATH = Path(DOC_STATIC_PATH, "PACF_plot")
#/****** Advanced ARIMA ******/

RESULT_PATH = Path(BASE_PATH, 'media_cdn', "result")
ZIPS_PATH = Path(BASE_PATH, 'media_cdn', "zips")
PERSIAN_PATH = Path(BASE_PATH, 'text_files', "Persian")
ENGLISH_PATH = Path(BASE_PATH, 'text_files', "English")

BATCH_SIZE = 1000


Thread_Count = 8

# ----------------------------------------------
LOCAL_HUGGINGFACE_CONFIGS = {
    "sentimentAnalyser":"local",
    "taggingAnalyser":"local",
    "classificationAnalyser":"local",
    "machineTranslator":"local",
    "summarizer":"local",
}
SERVER_HUGGINGFACE_CONFIGS = {
    "sentimentAnalyser":"global",
    "taggingAnalyser":"global",
    "classificationAnalyser":"global",
    "machineTranslator":"global",
    "summarizer":"global",
}

LOAD_MODELS = str(os.environ.get('LOAD_MODELS')) == 'true'
HUGGINGFACE_CONFIGS = SERVER_HUGGINGFACE_CONFIGS if (os.environ.get('LOAD_MODELS') is None or LOAD_MODELS) else LOCAL_HUGGINGFACE_CONFIGS
# HUGGINGFACE_CONFIGS = LOCAL_HUGGINGFACE_CONFIGS

# ----------------------------------------------
