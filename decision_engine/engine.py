def evaluate(status):

    if status == "NORMAL":
        return {
            "stable": True,
            "message": "Patient is clinically stable."
        }

    return {
        "stable": False,
        "message": "Patient requires medical attention."
    }