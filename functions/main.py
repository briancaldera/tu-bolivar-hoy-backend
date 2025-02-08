from firebase_functions import https_fn, options

@https_fn.on_request(cors=True)
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")
