# Imports
from scrape_utility import get_params, get_html
from cli_utility import print_bout
from rankings import get_rankings
import time

def print_event(title):
    # Retrieves UFC rankings
    rankings = get_rankings()

    # Retrieves parameters for the page specific to the event
    event_title = get_params(title)

    # Retrieves the event page HTML
    soup = get_html(event_title)
    tables = soup.find_all("table", {"class": "toccolours"})
    heading = soup.find("h2", id="Announced_bouts")

    # Tracker for maximum length of first fighter name
    max_first = 0

    # These 2 loops retrieve the maximum length of first fighter name
    # for pretty-printing
    if tables:
        scheduled_table = tables[0]
        for row in scheduled_table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            if len(cols) >= 4:
                weight = cols[0].get_text(" ", strip=True)
                fighter1 = cols[1].get_text(" ", strip=True)

                # Removes Wikipedia's champ tag
                if fighter1[-4:] == " (c)":
                    fighter1 = fighter1[:-4]

                fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
                max_first = max(max_first, len(fighter1))
    if heading is not None:
        ul = heading.find_next("ul")
        for li in ul.find_all("li"):
            bout_text = li.get_text(separator=" ", strip=True)
            weight = bout_text.split("bout:")[0].strip()
            fighter1 = bout_text.split("bout:")[1].split("vs.")[0].strip()
            fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
            max_first = max(max_first, len(fighter1))

    # Extra line
    print()

    # This loop pretty-prints the current fight card
    if tables:
        scheduled_table = tables[0]

        for row in scheduled_table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            if cols[0].get_text(" ", strip=True) == "Weight class":
                continue
            if len(cols) >= 4:
                weight = cols[0].get_text(" ", strip=True)
                fighter1 = cols[1].get_text(" ", strip=True)

                # Removes Wikipedia's champ tag
                if fighter1[-4:] == " (c)":
                    fighter1 = fighter1[:-4]

                fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
                fighter2 = cols[3].get_text(" ", strip=True)

                # Removes Wikipedia's champ tag
                if fighter2[-4:] == " (c)":
                    fighter2 = fighter1[:-4]

                fighter2 = rankings.get(weight + "_" + fighter2, "") + fighter2
                print_bout(weight, fighter1, fighter2, max_first)
            else:
                print()
                print(cols[0].get_text(" ", strip=True))
                print()

    # This loop pretty-prints the announced bouts
    if heading is not None:
        print()
        print("Announced bouts")
        print()
        ul = heading.find_next("ul")
        for li in ul.find_all("li"):
            bout_text = li.get_text(separator=" ", strip=True)
            weight = bout_text.split("bout:")[0].strip()
            fighter1 = bout_text.split("bout:")[1].split("vs.")[0].strip()
            fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
            fighter2 = bout_text.split("bout:")[1].split("vs.")[1].split("[")[0].strip()
            fighter2 = rankings.get(weight + "_" + fighter2, "") + fighter2
            print_bout(weight, fighter1, fighter2, max_first)

    # Sleeps for 1 second to avoid fast scrape requests
    time.sleep(1)