# Imports
from cli_utility import print_instruction, print_menu, test_input
from scrape_utility import get_params, get_html, get_title
from data_utility import print_event

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
    fixed_index = 0
    html_index = 0

    while fixed_index < 4:
        # Case where a previous row has an active rowspan
        if fixed_index in carry:
            values.append(carry[fixed_index]["text"])
            carry[fixed_index]["rows"] -= 1
            if carry[fixed_index]["rows"] == 0:
                del carry[fixed_index]
        else:
            if html_index < len(cols):
                cell = cols[html_index]
                text = cell.get_text(" ", strip=True)
                values.append(text)

                # Store rowspan if present
                rowspan = cell.get("rowspan")
                if rowspan and rowspan.isdigit() and int(rowspan) > 1:
                    carry[fixed_index] = {"text": text, "rows": int(rowspan) - 1}

                html_index += 1
            else:
                # No more columns left, but we still need values
                values.append("")
        fixed_index += 1

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

# Creates entry for new fights option
events.append({
    "event": "View Newly Announced Fights",
    "date": "",
    "venue": "",
    "location": "",
    "href": None
})

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

    if input_num == 0:
        printed_any = False
        for event in events:
            if event["event"] != "View Newly Announced Fights":
                # Retrieves event title from the href
                title = get_title(event["href"])

                printed_event = print_event(title, only_new = True)
                printed_any = printed_any or printed_event
        if not printed_any:
            print("All caught up!")
    else:
        # Retrieves event title from the href
        title = get_title(events[input_num]["href"])

        print_event(title)

    # Instructs user to return to menu and waits for input
    print()
    print("Please hit enter to continue")
    _ = input()

    # Prints the menu and waits for input
    print_menu(events, max_event, max_date, max_venue, max_location)
    command = input()