# Imports
from cli_utility import print_instruction, print_menu, print_bout, test_input
from scrape_utility import get_params, get_html, get_title
import time

# Retrieves parameters for the page listing upcoming events
list_of_events = get_params("List of UFC events")

# Retrieves upcoming events HTML
tables = get_html(list_of_events).find_all("table", {"class": "wikitable"})
scheduled_table = tables[0]

# Trackers for upcoming events and maximum lengths
events = []
max_event = 0
max_date = 0
max_venue = 0
max_location = 0

# Carryover for rowspans
carry = {}  # {col_index: {"text": str, "rows": int}}

# This loop retrieves the list of upcoming events
# and the maximum lengths of event names, dates, venues, and locations
for row in scheduled_table.find_all("tr")[1:]:  # skip header row
    cols = row.find_all(["td", "th"])
    values = []
    col_index = 0
    i = 0

    while col_index < 4:
        # Case where a previous row has an active rowspan
        if col_index in carry:
            values.append(carry[col_index]["text"])
            carry[col_index]["rows"] -= 1
            if carry[col_index]["rows"] == 0:
                del carry[col_index]
            col_index += 1
        else:
            if i < len(cols):
                cell = cols[i]
                text = cell.get_text(" ", strip=True)
                values.append(text)

                # Store rowspan if present
                rowspan = cell.get("rowspan")
                if rowspan and rowspan.isdigit() and int(rowspan) > 1:
                    carry[col_index] = {"text": text, "rows": int(rowspan) - 1}

                i += 1
                col_index += 1
            else:
                # No more columns left, but we still need values
                values.append("")
                col_index += 1

    # Unpack values
    event_name, date, venue, location = values

    # Get href for event
    td = row.find_all(["td", "th"])[0]
    a_tag = td.find("a")
    href = a_tag["href"] if a_tag and a_tag.has_attr("href") else None

    # Creates dictionary for event
    events.append({
        "event": event_name,
        "date": date,
        "venue": venue,
        "location": location,
        "href": href
    })

    # Update maximum lengths
    max_event = max(max_event, len(event_name))
    max_date = max(max_date, len(date))
    max_venue = max(max_venue, len(venue))
    max_location = max(max_location, len(location))

# Reverses events to get them in chronological order
events.reverse()

# Prints the menu and waits for input at start of program
print_menu(events, max_event, max_date, max_venue, max_location)
command = input()

# Continually prints the menu and waits for input until an invalid
# input is received (non-integer input)
while test_input(command) != "":
    # Converts input to integer
    input_num = int(command)

    # Error checks for integer inputs outside the valid range
    if input_num >= len(events) or input_num < 0:
        print_instruction(events)
        command = input()
        continue

    # Retrieves event title from the href
    title = get_title(events[input_num]["href"])

    # Retrieves parameters for the page specific to the event
    event_title = get_params(title)

    # Retrieves the event page HTML
    soup = get_html(event_title)
    tables = soup.find_all("table", {"class": "toccolours"})
    heading = soup.find("h2", id="Announced_bouts")

    # Tracker for maximum length of first fighter name
    _max_first = 0

    # These 2 loops retrieve the maximum length of first fighter name
    # for pretty-printing
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
                _weight = cols[0].get_text(" ", strip=True)
                _fighter1 = cols[1].get_text(" ", strip=True)
                _fighter2 = cols[3].get_text(" ", strip=True)
                print_bout(_weight, _fighter1, _fighter2, _max_first)
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
            _weight = bout_text.split("bout:")[0].strip()
            _fighter1 = bout_text.split("bout:")[1].split("vs.")[0].strip()
            _fighter2 = bout_text.split("bout:")[1].split("vs.")[1].split("[")[0].strip()
            print_bout(_weight, _fighter1, _fighter2, _max_first)

    # Sleeps for 1 second to avoid fast scrape requests
    time.sleep(1)

    # Instructs user to return to menu and waits for input
    print()
    print("Please hit enter to continue")
    _ = input()

    # Prints the menu and waits for input
    print_menu(events, max_event, max_date, max_venue, max_location)
    command = input()