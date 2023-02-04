# def query_builder(must: dict, must_not: dict, should: dict):
#     if len(must) + len(must_not) + len(should) == 0:
#         return {'match_all': []}
#     for key, value in must.items():
#         pass


def regex(pattern, field_name: str):
    clauses = []
    for keyword in pattern:
        if type(keyword) == int:
            continue
        if type(keyword) == str:
            clauses.append({"span_multi": {"match": {"regexp": {field_name: keyword}}}})
        else:
            sub_clauses = regex(keyword, field_name)
            if "span_near" in sub_clauses.keys() and len(sub_clauses["span_near"]['clauses']) == 0:
                continue
            if "span_or" in sub_clauses.keys() and len(sub_clauses["span_or"]['clauses']) == 0:
                continue
            if type(keyword) == tuple:
                clauses.append(sub_clauses)
            else:
                clauses.append(sub_clauses)
    if type(pattern) == tuple:
        return {"span_near": {"clauses": clauses, "slop": pattern[-1], "in_order": True}}
    else:
        return {"span_or": {"clauses": clauses}}
