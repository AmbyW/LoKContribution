# This is a sample Python script.
import requests
import json
from flask import Flask, render_template, request, jsonify


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
LOK_MAP = [i for i in range(100000, 165536)]


def get_adyacent_lands(land_number):
    try:
        land_number = int(land_number)
    except ValueError:
        pass
    if 100000 <= land_number <= 165535:
        prev_land = up_prev_land = down_prev_land = next_land = up_next_land = down_next_land = up_land = down_land = 0
        if (land_number - 100000) % 256 != 0:
            prev_land = land_number - 1
            if land_number > 100255:
                down_prev_land = land_number - 257
            if land_number < 165280:
                up_prev_land = land_number + 255
        if (land_number - 99999) % 256 != 0:
            next_land = land_number + 1
            if land_number < 165280:
                up_next_land = land_number + 257
            if land_number > 100255:
                down_next_land = land_number - 255
        if land_number < 165280:
            up_land = land_number + 256
        if land_number > 100255:
            down_land = land_number - 256
        return [
                {"position": 1, "id": up_prev_land},
                {"position": 2, "id": up_land},
                {"position": 3, "id": up_next_land},
                {"position": 4, "id": prev_land},
                {"position": 5, "id": land_number},
                {"position": 6, "id": next_land},
                {"position": 7, "id": down_prev_land},
                {"position": 8, "id": down_land},
                {"position": 9, "id": down_next_land},
        ]


def make_urls(land_number, from_date, to_date):
    urls = []
    for land in get_adyacent_lands(land_number):
        if land["id"] >= 100000:
            urls.append({"id": land["id"],
                         "position": land["position"],
                         "url": f"https://api-lok-live.leagueofkingdoms.com/api/stat/land/contribution?landId={land['id']}&from={from_date}&to={to_date}"})
    return urls


def get_lands_data(urls):
    responses = []
    for url in urls:
        response = requests.get(url["url"])
        if response.ok:
            content = json.loads(response.content.decode('utf-8'))
            if content["result"]:
                content["land_id"] = url["id"]
                responses.append(content)
    return responses


def get_land_contribution(data, kingdom_name):
    for kingdom in data:
        if kingdom["name"] == kingdom_name:
            return kingdom["total"]
    return 0


def process_lands_data(responses, urls, kingdom_name):
    lands = []
    owners = []
    for data in responses:
        exists_owner = False
        land = {
            "land": data["land_id"],
            "owner": data["owner"],
            "color": data["owner"][:8].replace("0x", "#"),
            "contribution": get_land_contribution(data["contribution"], kingdom_name),
        }
        for url in urls:
            if land["land"] == url["id"]:
                land["position"] = url["position"]
        lands.append(land)
        for owner in owners:
            exists_owner = False
            if land["owner"] == owner["wallet"]:
                owner["contribution"] += land["contribution"]
                exists_owner = True
                break
        if not exists_owner:
            owners.append({"wallet": land["owner"], "contribution": land["contribution"]})
    return {"lands": lands, "owners": owners}


flask_app = Flask(__name__)


@flask_app.route('/get_contribution', methods=['GET'])
def get_contribution():
    kingdom = request.args.get("kingdom_name")
    land = request.args.get("land_id")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    # print(kingdom, land, from_date, to_date)
    # response = {"mssage": "todo ok"}
    urls = make_urls(land, from_date, to_date)
    responses = get_lands_data(urls)
    response = process_lands_data(responses, urls, kingdom)
    return jsonify(response), 200


@flask_app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
