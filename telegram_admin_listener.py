# ==========================
# GET UPDATES
# ==========================

def get_updates():

    global offset


    params = {

        "timeout": 30,

        "allowed_updates": [

            "message",

            "callback_query"

        ]

    }


    if offset:

        params["offset"] = offset



    try:


        r = requests.get(

            f"{API_URL}/getUpdates",

            params=params,

            timeout=35

        )



        data = r.json()



        print(

            "GET UPDATES:",

            data,

            flush=True

        )



        return data



    except Exception as e:


        print(

            "GET UPDATES ERROR:",

            e,

            flush=True

        )


        return {}
