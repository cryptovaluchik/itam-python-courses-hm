from requests import get

def is_valid_link(link: str) -> bool:

    try:
        response = get(url=link)
    except Exception:
        return False

    return True 


# result = is_valid_link(
#     link="https://edu.itatmisis.ru/c/2025/autumn/python/homeworks/1fb6cec1-a6a9-44fb-818d-be54db25066b"
# )

# print(result)