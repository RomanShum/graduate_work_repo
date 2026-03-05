from typing import List


def create_query_by_elastic(sort, page_number, page_size, query):
    result = {
        "from": (page_number - 1) * page_size,
        "size": page_size,
    }
    if sort:
        direction = "DESC" if sort.startswith('-') else "ASC"
        sort = sort[1:] if sort.startswith('-') else sort
        result['sort'] = {f"{sort}": {"order": direction}}

    if query:
        result['query'] = {
            "multi_match": {
                "query": f"{query}",
                "fuzziness": "auto",
                "fields": ["title"]
            }
        }
    return result


def get_key(params: List):
    list_string = [str(item) for item in params]
    string_key = '_'.join(list_string)
    hash_key = hash(string_key)
    return str(hash_key)
