# Imports
from scrape_utility import get_params, get_html
from cli_utility import return_bout
from rankings import get_rankings
import shelve
import time

# This function iterates through the webpage for a particular
# UFC event in order to print out the full card
def print_event(title, only_new = False):
    # Retrieves UFC rankings
    rankings = get_rankings()

    # Retrieves parameters for the page specific to the event
    event_title = get_params(title)

    title = title.replace('_', ' ')

    # Tracker for only_new printing
    printed_title = False

    # Retrieves the event page HTML
    soup = get_html(event_title)
    tables = soup.find_all("table", {"class": "toccolours"})
    heading = soup.find("h2", id="Announced_bouts")

    # Tracker for maximum length of first fighter name
    max_first = get_max_fighter1(tables, heading, rankings)

    # Extra line
    if not only_new:
        print()

    # Gets already-seen fights for this event
    with shelve.open("Events") as prefs:
        stored = prefs.get(title, [])
        stored_for_cancellations = prefs.get(title, [])

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
                fighter2 = cols[3].get_text(" ", strip=True)

                # Removes Wikipedia's champ tag
                if fighter1[-4:] == " (c)":
                    fighter1 = fighter1[:-4]

                # Removes Wikipedia's champ tag
                if fighter2[-4:] == " (c)":
                    fighter2 = fighter1[:-4]

                if not only_new:
                    # Adds ranking tags
                    fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
                    fighter2 = rankings.get(weight + "_" + fighter2, "") + fighter2
                    bout = return_bout(weight, fighter1, fighter2, max_first)
                    print(bout, flush=True)
                else:
                    bout = return_bout(weight, fighter1, fighter2, max_first)
                    if not bout in stored:
                        if not printed_title:
                            print()
                            print(title)
                            print()
                            print("Additions:")
                            print()
                            printed_title = True

                        stored.append(bout)
                        with shelve.open("Events") as prefs:
                            prefs[title] = stored
                        fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
                        fighter2 = rankings.get(weight + "_" + fighter2, "") + fighter2
                        bout = return_bout(weight, fighter1, fighter2, max_first)
                        print(bout, flush=True)
                    else:
                        stored_for_cancellations.remove(bout)
            elif not only_new:
                print()
                print(cols[0].get_text(" ", strip=True))
                print()

    # This loop pretty-prints the announced bouts
    if heading is not None:
        if not only_new:
            print()
            print("Announced bouts")
            print()
        ul = heading.find_next("ul")
        for li in ul.find_all("li"):
            bout_text = li.get_text(separator=" ", strip=True)
            weight = bout_text.split("bout:")[0].strip()
            fighter1 = bout_text.split("bout:")[1].split("vs.")[0].strip()
            fighter2 = bout_text.split("bout:")[1].split("vs.")[1].split("[")[0].strip()

            # Removes Wikipedia's champ tag
            if fighter1[-4:] == " (c)":
                fighter1 = fighter1[:-4]

            # Removes Wikipedia's champ tag
            if fighter2[-4:] == " (c)":
                fighter2 = fighter1[:-4]

            if not only_new:
                # Adds ranking tags
                fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
                fighter2 = rankings.get(weight + "_" + fighter2, "") + fighter2
                bout = return_bout(weight, fighter1, fighter2, max_first)
                print(bout, flush=True)
            else:
                bout = return_bout(weight, fighter1, fighter2, max_first)
                if not bout in stored:
                    if not printed_title:
                        print()
                        print(title)
                        print()
                        print("Additions:")
                        print()
                        printed_title = True

                    stored.append(bout)
                    with shelve.open("Events") as prefs:
                        prefs[title] = stored
                    fighter1 = rankings.get(weight + "_" + fighter1, "") + fighter1
                    fighter2 = rankings.get(weight + "_" + fighter2, "") + fighter2
                    bout = return_bout(weight, fighter1, fighter2, max_first)
                    print(bout, flush=True)
                else:
                    stored_for_cancellations.remove(bout)

    # Prints cancelled bouts
    if only_new and stored_for_cancellations:
        if not printed_title:
            print()
            print(title)
            printed_title = True
        print()
        print("Cancellations:")
        print()
        for bout in stored_for_cancellations:
            stored.remove(bout)
            with shelve.open("Events") as prefs:
                prefs[title] = stored
            print(bout, flush=True)

    # Sleeps for 1 second to avoid fast scrape requests
    time.sleep(1)

    return printed_title

# This function retrieve the maximum length of first fighter name
# for pretty-printing
def get_max_fighter1(tables, heading, rankings):
    # Tracker for maximum length of first fighter name
    max_first = 0

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

    return max_first