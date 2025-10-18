from requests import get

def is_valid_link(link: str) -> bool:

    response = get(
        url=link
    )

    status_code = response.status_code

    if 200 <= status_code < 300:
        return True
    
    return False


# result = is_valid_link(
#     link="https://edu.itatmisis.ru/c/2025/autumn/python/homeworks/1fb6cec1-a6a9-44fb-818d-be54db25066b"
# )

# print(result)