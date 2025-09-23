import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import time

def get_params(page):
    return {
        "action": "parse",
        "page": page,
        "format": "json",
        "prop": "text"
    }

URL = "https://en.wikipedia.org/w/api.php"
starter = "https://en.wikipedia.org"

params = get_params("List of UFC events")

headers = {
    "User-Agent": "UFCFightNews/0.1 (jchirsch@umich.edu)"
}

r = requests.get(URL, params=params, headers=headers)
data = r.json()

html = data["parse"]["text"]["*"]

soup = BeautifulSoup(html, "html.parser")

tables = soup.find_all("table", {"class": "wikitable"})
scheduled_table = tables[0]

events = []
max_event = 0
max_date = 0
max_venue = 0
max_location = 0

for row in scheduled_table.find_all("tr")[1:]: # skip header row
    cols = row.find_all(["td", "th"])
    if len(cols) >= 4:
        td = cols[0]
        a_tag = td.find("a")
        href = None
        if a_tag and a_tag.has_attr("href"):
            href = a_tag["href"]
        event_name = cols[0].get_text(" ", strip=True)
        date = cols[1].get_text(" ", strip=True)
        venue = cols[2].get_text(" ", strip=True)
        location = cols[3].get_text(" ", strip=True)
        events.append({
            "event": event_name,
            "date": date,
            "venue": venue,
            "location": location,
            "href": href
        })
        max_event = max(max_event, len(event_name))
        max_date = max(max_date, len(date))
        max_venue = max(max_venue, len(venue))
        max_location = max(max_location, len(location))

events.reverse()

def print_instruction():
    print(f"Type a number from 0-{len(events) - 1} to see the announced fights for a particular event.")

def print_menu():
    print_instruction()
    print("#".rjust(len(str(len(events))), " ").ljust(len(str(len(events))) + 3, " "), end='')
    print("Event".ljust(max_event + 3, " "), end='')
    print("Date".ljust(max_date + 3, " "), end='')
    print("Venue".ljust(max_venue + 3, " "), end='')
    print("Location".ljust(max_location + 3, " "))

    for num, e in enumerate(events):
        print(str(num).rjust(len(str(len(events))), " ").ljust(len(str(len(events))) + 3, " "), end='')
        print(e["event"].ljust(max_event + 3, " "), end='')
        print(e["date"].ljust(max_date + 3, " "), end='')
        print(e["venue"].ljust(max_venue + 3, " "), end='')
        print(e["location"].ljust(max_location + 3, " "))

def test_input(x):
    try:
        return int(x)
    except ValueError:
        return ""

def get_title(link):
    if link.startswith("/wiki/"):
        return unquote(link.split("/wiki/")[-1].split("#")[0])
    return None

def print_bout(weight, fighter1, fighter2, max_first):
    print(weight.ljust(23, " "), end='')
    print(fighter1.rjust(max_first, " "), end=' ')
    print("vs.", end=' ')
    print(fighter2)

print_menu()
command = input()

while test_input(command) != "":
    input_num = int(command)

    if input_num >= len(events) or input_num < 0:
        print_instruction()
        command = input()
        continue

    print()
    title = get_title(events[input_num]["href"])
    r = requests.get(URL, params=get_params(title), headers=headers)
    data = r.json()
    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", {"class": "toccolours"})
    heading = soup.find("h2", id="Announced_bouts")

    _max_first = 0
    if tables:
        scheduled_table = tables[0]
        for row in scheduled_table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            if len(cols) >= 4:
                _fighter1 = cols[1].get_text(" ", strip=True)
                _max_first = max(_max_first, len(_fighter1))
    if heading is not None:
        ul = heading.find_next("ul")
        for li in ul.find_all("li"):
            bout_text = li.get_text(separator=" ", strip=True)
            _fighter1 = bout_text.split("bout:")[1].split("vs.")[0].strip()
            _max_first = max(_max_first, len(_fighter1))

    if tables:
        scheduled_table = tables[0]

        for row in scheduled_table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            if cols[0].get_text(" ", strip=True) == "Weight class":
                continue
            if len(cols) >= 4:
                _weight = cols[0].get_text(" ", strip=True)
                _fighter1 = cols[1].get_text(" ", strip=True)
                _fighter2 = cols[3].get_text(" ", strip=True)
                print_bout(_weight, _fighter1, _fighter2, _max_first)
            else:
                print()
                print(cols[0].get_text(" ", strip=True))
                print()

    if heading is not None:
        print()
        print("Announced bouts")
        print()
        ul = heading.find_next("ul")
        for li in ul.find_all("li"):
            bout_text = li.get_text(separator=" ", strip=True)
            _weight = bout_text.split("bout:")[0].strip()
            _fighter1 = bout_text.split("bout:")[1].split("vs.")[0].strip()
            _fighter2 = bout_text.split("bout:")[1].split("vs.")[1].split("[")[0].strip()
            print_bout(_weight, _fighter1, _fighter2, _max_first)

    time.sleep(1)
    print()
    print("Please hit enter to continue")
    _ = input()

    print_menu()
    command = input()