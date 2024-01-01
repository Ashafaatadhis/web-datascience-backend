from flask import jsonify

class GetDto :
    def __init__():
        pass

    def getDto(data, status):
        return jsonify({"data": data, "success":status})