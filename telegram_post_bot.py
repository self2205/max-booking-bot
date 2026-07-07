import requests

from config import TG_POST_TOKEN


API_URL = (
    f"https://api.telegram.org/bot{TG_POST_TOKEN}"
)


def get_updates():

    r = requests.get(
        f"{API_URL}/getUpdates",
        timeout=30
    )

    data = r.json()

    print(data)



if __name__ == "__main__":

    get_updates()
