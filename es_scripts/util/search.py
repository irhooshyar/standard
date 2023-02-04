SEARCH_WINDOW_SIZE = 5000
SEARCH_MAX_SIZE = 10000


def search_size_all(client, **kwargs):
    result = {"hits": {"total": {"value": 0}, "hits": []}}
    from_ = 0
    response = client.search(**kwargs, size=SEARCH_WINDOW_SIZE, from_=from_)
    while len(response['hits']['hits']) != 0:
        result['hits']['hits'] += response['hits']['hits']
        if response['hits']['total']['value'] <= SEARCH_WINDOW_SIZE:
            break
        from_ += SEARCH_WINDOW_SIZE
        response = client.search(**kwargs, size=SEARCH_WINDOW_SIZE, from_=from_)
    result['hits']['total']['value'] = len(result['hits']['hits'])
    return result
