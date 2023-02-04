import os

ES_URL = os.environ.get('ES_URL')
if ES_URL is None:
    # ES_URL = "37.156.144.109:9602"
    ES_URL = "192.168.50.8:9200"

INGEST_ENABLED = False

BUCKET_SIZE = 1000
SEARCH_RESULT_SIZE = 500

DOTIC_DOC_INDEX = "doticfull_document"
DOTIC_PARA_INDEX = "doticfull_documentparagraphs_graph"

Book_Index = "book_search_index"

Paragraphs_Settings = {
    "analysis": {
        "filter": {
            "persian_stop_file": {
                "type": "stop",
                "stopwords_path": "persian_stopwords.txt"
            },
            "cybermap_stop_file": {
                "type": "stop",
                "stopwords_path": "cybermap_stopwords.txt"
            },
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],

                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "arabic_stop",
                    "persian_stop",
                    "english_stop",
                    "persian_stop_file",
                    "cybermap_stop_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}

Paragraphs_Settings_3 = {
    "analysis": {
        "filter": {
            "all_stopwords_file": {
                "type": "stop",
                "stopwords_path": "all_stopwords.txt"
            },
            "rahbari_stopwords_file": {
                "type": "stop",
                "stopwords_path": "rahbari_stopwords.txt"
            },
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],

                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "arabic_stop",
                    "persian_stop",
                    "english_stop",
                    "all_stopwords_file",
                    "rahbari_stopwords_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}


Paragraphs_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "approval_year": {
            "type": "integer"
        },

        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "clause_type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "clause_number": {
            "type": "integer"
        },

        "paragraph_id": {
            "type": "integer"
        },
        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

Paragraphs_Settings_2 = {
    "analysis": {
        "filter": {
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],

                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}

# -----------------------------------------------

Clustering_Paragraphs_Settings = {
    "analysis": {
        "filter": {
            "all_stopwords_file": {
                "type": "stop",
                "stopwords_path": "all_stopwords.txt"
            },
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],

                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "all_stopwords_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "200000"
}

Clustering_Paragraphs_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "keyword_subject": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "approval_year": {
            "type": "integer"
        },

        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "paragraph_id": {
            "type": "integer"
        },
        "topic_id": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "topic_name": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "topic_score": {
            "type": "integer"
        },
        "data": {
            "type": "text"
        },
        "preprocessed_text": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

Document_Actor_Settings = {
    "analysis": {
        "filter": {
            "persian_stop_file": {
                "type": "stop",
                "stopwords_path": "persian_stopwords.txt"
            },
            "cybermap_stop_file": {
                "type": "stop",
                "stopwords_path": "cybermap_stopwords.txt"
            },
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],

                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "arabic_stop",
                    "persian_stop",
                    "english_stop",
                    "persian_stop_file",
                    "cybermap_stop_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}

Document_Actor_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "document_subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "document_approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "document_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "document_level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "document_revoked_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "document_organization_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 512
                }
            }
        },
        "document_approval_year": {
            "type": "integer"
        },
        "document_advisory_opinion_count": {
            "type": "integer"
        },
        "document_interpretation_rules_count": {
            "type": "integer"
        },
        "paragraph_id": {
            "type": "integer"
        },
        "duty_type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "actor_id": {
            "type": "integer"
        },
        "actor_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "actor_category_id": {
            "type": "integer"
        },
        "actor_category_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "actor_area_id": {
            "type": "integer"
        },
        "actor_area_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        # "actor_sub_area_id": {
        #     "type": "integer"
        # },
        # "actor_sub_area_name": {
        #     "type": "text",
        #     "analyzer": "persian_custom_analyzer",
        #     "fields": {
        #         "keyword": {
        #             "type": "keyword",
        #             "ignore_above": 256
        #         }
        #     }
        # },
        "actor_type_id": {
            "type": "integer"
        },
        "actor_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "current_actor_form": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "general_definition_keyword": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "general_definition_text": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "ref_paragraph_text": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

Standard_BM25_Settings = {
    "analysis": {
        "filter": {
            "all_stopwords_file": {
                "type": "stop",
                "stopwords_path": "all_stopwords.txt"
            },
            "rahbari_stopwords_file": {
                "type": "stop",
                "stopwords_path": "rahbari_stopwords.txt"
            },
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],

                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "arabic_stop",
                    "persian_stop",
                    "english_stop",
                    "all_stopwords_file",
                    "rahbari_stopwords_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}

BM25_Standard_Mappings = {
    "properties": {
        "approval_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },

        "file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "subject": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "standard_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "branch": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "subject_category": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "ICS": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "status": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "appeal_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "Description": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

Standard_DFR_Settings = {
    "analysis": {
        "filter": {
            "persian_stop_file": {
                "type": "stop",
                "stopwords_path": "persian_stopwords.txt"
            },
            "cybermap_stop_file": {
                "type": "stop",
                "stopwords_path": "cybermap_stopwords.txt"
            },
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"
            }
        },
        "analyzer": {
            "persian_custom_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],
                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "arabic_stop",
                    "persian_stop",
                    "english_stop",
                    "persian_stop_file",
                    "cybermap_stop_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000",
    "similarity": {
        "DFR_SIM": {
            "type": "DFR",
            "basic_model": "g",
            "after_effect": "l",
            "normalization": "h2",
            "normalization.h2.c": "3.0"
        }

    }
}

DFR_Standard_Mappings = {
    "properties": {
        "approval_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },

        "file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "subject": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "standard_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "branch": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "ICS": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "status": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "appeal_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "Description": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "similarity": "DFR_SIM",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

Standard_DFI_Settings = {
    "analysis": {
        "filter": {
            "persian_stop_file": {
                "type": "stop",
                "stopwords_path": "persian_stopwords.txt"
            },
            "cybermap_stop_file": {
                "type": "stop",
                "stopwords_path": "cybermap_stopwords.txt"
            },
            "persian_stop": {
                "type": "stop",
                "stopwords": "_persian_"
            },
            "arabic_stop": {
                "type": "stop",
                "stopwords": "_arabic_"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            }
        },
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"
            }
        },
        "analyzer": {
            "persian_custom_analyzer": {

                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],
                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer",
                    "arabic_stop",
                    "persian_stop",
                    "english_stop",
                    "persian_stop_file",
                    "cybermap_stop_file"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000",
    "similarity": {
        "DFI_SIM": {
            "type": "DFI",
            "independence_measure": "standardized"
        }
    }

}

DFI_Standard_Mappings = {
    "properties": {
        "approval_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },

        "file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "subject": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "standard_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "branch": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "ICS": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "status": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "appeal_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "Description": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",
                    "similarity": "DFI_SIM",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

FA_Settings = {
    "analysis": {
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings_path": "char_filter/zero_width_spaces_filter.txt"

            }
        },
        "analyzer": {
            "persian_custom_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "char_filter": [
                    "zero_width_spaces"
                ],
                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "parsi_normalizer"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}

FA_Mappings = {
    "properties": {
        "approval_date": {
            "type": "text"
        },
        "approval_year": {
            "type": "integer"
        },
        "communicated_date": {
            "type": "text"
        },
        "communicated_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "advisory_opinion_count": {
            "type": "integer"
        },
        "interpretation_rules_count": {
            "type": "integer"
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "raw_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "standard_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "revoked_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "organization_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 512
                }
            }
        },

        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "term_vector": "with_positions_offsets",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "subject_weight": {
            "type": "text"
        },

        "type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "subject_area": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "subject_sub_area": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "subject_sub_area_weight": {
            "type": "text"
        },

        "subject_sub_area_entropy": {
            "type": "text"
        },

        "revoked_sub_type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "revoked_size": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "revoked_clauses": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

FA_BM25_Mappings = {
    "properties": {
        "approval_date": {
            "type": "text"
        },
        "approval_year": {
            "type": "integer"
        },
        "communicated_date": {
            "type": "text"
        },
        "communicated_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "advisory_opinion_count": {
            "type": "integer"
        },
        "interpretation_rules_count": {
            "type": "integer"
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "raw_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "standard_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "revoked_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "organization_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
        },

        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",

                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

FA_DFR_Mappings = {
    "properties": {
        "approval_date": {
            "type": "text"
        },
        "approval_year": {
            "type": "integer"
        },
        "communicated_date": {
            "type": "text"
        },
        "communicated_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "advisory_opinion_count": {
            "type": "integer"
        },
        "interpretation_rules_count": {
            "type": "integer"
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "raw_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "standard_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "revoked_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "organization_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            # "fields": {
            #     "keyword": {
            #         "type": "keyword",
            #         "ignore_above": 256
            #     }
            # }
        },

        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",
                    "similarity": "DFR_SIM",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

FA_DFI_Mappings = {
    "properties": {
        "approval_date": {
            "type": "text"
        },
        "approval_year": {
            "type": "integer"
        },
        "communicated_date": {
            "type": "text"
        },
        "communicated_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "advisory_opinion_count": {
            "type": "integer"
        },
        "interpretation_rules_count": {
            "type": "integer"
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "raw_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "standard_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "revoked_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "organization_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            # "fields": {
            #     "keyword": {
            #         "type": "keyword",
            #         "ignore_above": 256
            #     }
            # }
        },

        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",
                    "similarity": "DFI_SIM",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

EN_Settings = {
    "analysis": {
        "analyzer": {
            "english_custom_analyzer": {
                "tokenizer": "classic",
                "filter": [
                    "lowercase",
                    "decimal_digit"
                ]
            }
        }
    },
    "number_of_shards": 5,
    "number_of_replicas": 0,
    "refresh_interval": "-1",
    "index.max_result_window": "5000"
}

EN_Mappings = {
    "properties": {
        "approval_date": {
            "type": "integer"
        },
        "approval_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "raw_file_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer"
        },

        "level_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "name": {
            "type": "text",
            "analyzer": "english_custom_analyzer"
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "english_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

EN_Paragraphs_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer"
        },
        "type_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "approval_reference_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "approval_year": {
            "type": "integer"
        },

        "level_name": {
            "type": "text",
            "analyzer": "english_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "paragraph_id": {
            "type": "integer"
        },
        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "analyzer": "english_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}
# -----------------------------------------------

Standard_Mappings = {
    "properties": {
        "approval_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },

        "file_name_with_extention": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "standard_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "branch": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "ICS": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "status": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "appeal_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "Description": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

Judement_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "document_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "judgment_id": {
            "type": "integer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "judgment_number": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "judgment_date": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "judgment_year": {
            "type": "integer"
        },
        "complaint_serial": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "conclusion_display_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "subject_type_display_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "judgment_type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "complainant": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "complaint_from": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "subject_complaint": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }

        },
        "categories": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "affected_document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

Terminology_Mappings = {
    "properties": {
        "def_id": {
            "type": "integer",
        },
        "keyword": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "text": {
            "type": "text",
        },
        "is_abbreviation": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
        },
        "document_approval_date": {
            "type": "text"
        },
        "document_approval_reference_name": {
            "type": "text"
        },
        "document_level_name": {
            "type": "text"
        },
        "document_subject_name": {
            "type": "text"
        },
    }
}

# -----------------------------------------------

Revoked_Mappings = {
    "properties": {
        "approval_year": {
            "type": "integer"
        },
        "src_document_id": {
            "type": "integer"
        },
        "src_document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "dest_document_id": {
            "type": "integer"
        },
        "dest_document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "dest_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "revoked_type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "subject_area_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "subject_sub_area_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "revoked_sub_type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "revoked_size": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "revoked_clauses": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "src_para_id": {
            "type": "integer"
        },
        "dest_para_id": {
            "type": "integer"
        },

        "src_approval_date": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "dest_approval_date": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "level_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        
        "type_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}
# ------------------  Geo --------------------------------
# yyyyMMdd'T'HHmmssZ
Geo_Mappings = {
    "properties": {
        "name": {
            "type": "text",
            "analyzer": "english_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "date_time": {
            "type": "date"
        },

        "location": {
            "type": "geo_point"
        }
    }
}

# ------------------  Rahbari --------------------------------

Rahbari_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "raw_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "rahbari_date": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "rahbari_year": {
            "type": "integer"
        },
        "labels": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "rahbari_type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "approval_reference_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "approval_date": {
            "type": "text"
        },
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        

        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# --------- Rahbari Similarity Indices ----------------------

BM25_Rahbari_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "document_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "rahbari_date": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "rahbari_year": {
            "type": "integer"
        },
        "labels": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

DFR_Rahbari_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "document_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "rahbari_date": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "rahbari_year": {
            "type": "integer"
        },
        "labels": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "term_vector": "with_positions_offsets",
                    "similarity": "DFR_SIM",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

DFI_Rahbari_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "document_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "rahbari_date": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "rahbari_year": {
            "type": "integer"
        },
        "labels": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "data": {
            "type": "text"
        },

        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "term_vector": "with_positions_offsets",
                    "similarity": "DFI_SIM",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# --------------- DocumentCollectiveMembers ---------------------
DocumentCollectiveMembers_Mappings = {
    "properties": {
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "document_approval_date": {
            "type": "text"
        },
        "document_approval_year": {
            "type": "integer"
        },
        "document_approval_reference_name": {
            "type": "text"
        },
        "document_level_name": {
            "type": "text"
        },
        "document_subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "paragraph_id": {
            "type": "integer"
        },
        "paragraph_text": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },
        "paragraph_number": {
            "type": "integer"
        },
        "collective_actor_id": {
            "type": "integer"
        },
        "collective_actor_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "members": {
            "properties": {
                "id": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "form": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
            }
        },
        "members_count": {
            "type": "integer"
        },
        "has_next_paragraph_members": {
            "type": "boolean"
        },
        "next_paragraphs": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "obligation": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# -----------------------------------------------

ActorSupervisor_Mappings = {
    "properties": {
        "id": {
            "type": "integer",
        },
        "source_actor_id": {
            "type": "integer",
        },
        "source_actor_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "supervisor_actor_id": {
            "type": "integer",
        },
        "supervisor_actor_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "source_actor_form": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "supervisor_actor_form": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "paragraph_id": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}

# --------- Sentiment --------------------
FullProfileAnalysis_Mappings = {
    "properties": {
        "sentiment": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "classification_subject": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "persons": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "locations": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "organizations": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 1024
                        }
                    }
                },
        "rahbari_date": {
            "type": "text",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "rahbari_year": {
            "type": "integer"
        },
        "labels": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "type": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        "data": {
            "type": "text"
        },
        "paragraph_id": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "document_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}


Book_Mappings = {
    "properties": {

        "published_year": {
            "type": "integer"
        },
        "document_id": {
            "type": "integer"
        },
        "pages_count": {
            "type": "integer"
        },

        "raw_file_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer"
        },

        "publisher_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "status": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },

        "book_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "term_vector": "with_positions_offsets",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 1024
                }
            }
        },
        
        "subject_name": {
            "type": "text",
            "analyzer": "persian_custom_analyzer",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },

        "data": {
            "type": "text"
        },
        "attachment": {
            "properties": {
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "persian_custom_analyzer",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content_length": {
                    "type": "long"
                },
                "content_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "date": {
                    "type": "date"
                },
                "language": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }
}
