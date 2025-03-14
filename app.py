# This is a sample Python script.
import datetime
import requests
import json
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
LOK_MAP = [i for i in range(100000, 165536)]


def get_adyacent_lands(land_number, adjacent_lands):
    try:
        land_number = int(land_number)
    except ValueError:
        pass
    if 100000 <= land_number <= 165535:
        prev_land = (
            up_prev_land
        ) = (
            down_prev_land
        ) = next_land = up_next_land = down_next_land = up_land = down_land = 0
        if adjacent_lands:
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


def get_date_ranges(from_date, to_date):
    date_starts = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    date_ends = datetime.datetime.strptime(to_date, "%Y-%m-%d")
    date_range = abs(date_starts - date_ends) + datetime.timedelta(days=1)
    if date_range.days < 7:
        return [
            (from_date, to_date),
        ]
    range_date_days = date_range.days
    date_list = []
    while range_date_days > 0:
        next_days = 7 if range_date_days >= 7 else range_date_days
        range_date_days -= next_days
        date_list.append(
            (
                date_starts.strftime("%Y-%m-%d"),
                (date_starts + datetime.timedelta(days=next_days - 1)).strftime(
                    "%Y-%m-%d"
                ),
            )
        )
        date_starts += datetime.timedelta(days=next_days)
    return date_list


def make_urls(land_number, from_date, to_date, adjacent_lands=False):
    urls = []
    for land in get_adyacent_lands(land_number, adjacent_lands):
        for date_start, date_end in get_date_ranges(from_date, to_date):
            if land["id"] >= 100000:
                urls.append(
                    {
                        "id": land["id"],
                        "position": land["position"],
                        "url": f"https://api-lok-live.leagueofkingdoms.com/api/stat/land/contribution?landId={land['id']}&from={date_start}&to={date_end}",
                    }
                )
    return urls


def get_lands_data(urls):
    responses = []

    def make_requests(url: dict):
        response = requests.get(url.get("url", ""))
        if response.ok:
            content = json.loads(response.content.decode("utf-8"))
            content["land_id"] = url.get("id", 0)
            responses.append(content)

    threads_list = []
    threads = len(urls)
    for thread_number in range(threads):
        thread = threading.Thread(
            name=f"requesting_url_no_{thread_number}",
            target=make_requests,
            args=(urls[thread_number],),
        )
        threads_list.append(thread)
        thread.start()

    for thread in threads_list:
        thread.join()

    return responses


def get_land_contribution(data, kingdom_name):
    for kingdom in data:
        if kingdom["name"] == kingdom_name:
            return kingdom.get("total", 0)
    return 0


def process_lands_data(responses, urls):
    lands_contributions = {}
    owner_contributions = {}
    kingdoms = {}
    for data in responses:
        if data.get("result", False):
            wallet = data.get("owner", "0x0000000000")
            land = lands_contributions.get(
                data.get("land_id"),
                {
                    "contributions": [],
                    "land": data.get("land_id", 0),
                    "owner": wallet,
                    "color": wallet[:8].replace("0x", "#"),
                },
            )
            if not land.get("position"):
                for url in urls:
                    if land["land"] == url.get("id", 0):
                        land["position"] = url.get(
                            "position",
                        )
            wallet_owner_contribution = owner_contributions.get(wallet, {})
            for kingdom_contribution in data.get("contribution", []):
                kingdom_id = kingdom_contribution.get("kingdomId", "")
                if not (kingdom_name := kingdom_contribution.get("name", "")) in kingdoms.keys():
                    kingdoms[kingdom_name] = {"id": kingdom_id,
                                              "text": kingdom_name,
                                              "continent": kingdom_contribution.get("continent", 0), }
                contribution = kingdom_contribution.get("total", 0)
                contribution_founded = False
                for land_kingdom_contribution in land["contributions"]:
                    if land_kingdom_contribution["kingdomId"] == kingdom_id:
                        land_kingdom_contribution["contribution"] += contribution
                        contribution_founded = True
                        break
                if not contribution_founded:
                    land_kingdom_contribution = {
                        "kingdomId": kingdom_id,
                        "contribution": contribution
                    }
                    land["contributions"].append(land_kingdom_contribution)
                total = wallet_owner_contribution.get(kingdom_id, 0) + contribution
                wallet_owner_contribution[kingdom_id] = total

            lands_contributions[data.get("land_id")] = land
            owner_contributions[wallet] = wallet_owner_contribution
        else:
            land = lands_contributions.get(
                data.get("land_id"),
                {
                    "contribution": 0,
                    "land": data.get("land_id", 0),
                    "owner": "No Owner"
                    if data.get("err", {}).get("code", "") == "no_land_owner"
                    else data.get("error", {}).get("code", ""),
                    "color": "#bd6c1e"
                    if data.get("err", {}).get("code", "") == "no_land_owner"
                    else "#FFFFFF00",
                },
            )
            if not land.get("position"):
                for url in urls:
                    if land["land"] == url.get("id", 0):
                        land["position"] = url.get(
                            "position",
                        )
                        # break
            lands_contributions[data.get("land_id")] = land
    return {
        "lands": [land for land in lands_contributions.values()],
        "owners": [
            {"wallet": key, "contributions": value}
            for key, value in owner_contributions.items()
        ],
        "kingdoms": [k for k in kingdoms.values()],
    }


flask_app = Flask(__name__)


@flask_app.route("/get_contribution", methods=["GET"])
def get_contribution():
    land = request.args.get("land_id")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    adjacent_lands = True if request.args.get("adjacent_lands") == "true" else False
    urls = make_urls(land, from_date, to_date, adjacent_lands)
    responses = get_lands_data(urls)
    response = process_lands_data(responses, urls)
    return jsonify(response), 200


@flask_app.route("/assets/<path:path>", methods=["GET"])
def send_assets(path):
    return send_from_directory("static", path)


@flask_app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
