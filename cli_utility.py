# This function prints the instructions
def print_instruction(events):
    print(f"Type a number from 0-{len(events) - 1} to see the announced fights for a particular event.")

# This function prints the full menu
def print_menu(events, max_event, max_date, max_venue, max_location):
    print_instruction(events)
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

# This function pretty-prints one bout
def print_bout(weight, fighter1, fighter2, max_first):
    print(weight.ljust(23, " "), end='')
    print(fighter1.rjust(max_first, " "), end=' ')
    print("vs.", end=' ')
    print(fighter2)

# This function tests whether the input is an integer
def test_input(x):
    try:
        return int(x)
    except ValueError:
        return ""