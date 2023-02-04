FROM elasticsearch:7.13.1

# RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch license
# RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install shield
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch ingest-attachment
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install https://www.dropbox.com/s/cr61dmnx95taivi/ParsiAnalyzer-7.13.1.zip?dl=1
# RUN /usr/share/elasticsearch/bin/elasticsearch-plugin --batch watcher
# RUN /usr/share/elasticsearch/bin/elasticsearch-plugin --batch royrusso/elasticsearch-HQ
#PUT _ingest/pipeline/attachment
#{
#  "description" : "Extract attachment information",
#  "processors" : [
#    {
#      "attachment" : {
#        "field" : "data",
#        "indexed_chars" : -1
#      }
#    }
#  ]
#}