# Imports
from scrape_utility import get_params, get_html

def get_rankings():
    # Retrieves parameters for the UFC rankings page
    rankings_params = get_params("UFC_rankings")

    # Retrieves ranking tables
    tables = get_html(rankings_params).find_all("table", {"class": "wikitable"})
    tables.remove(tables[0])
    tables.remove(tables[0])
    tables.remove(tables[0])

    # Weight classes in order as they appear on Wikipedia
    weight_classes = ["Heavyweight",
                      "Light Heavyweight",
                      "Middleweight",
                      "Welterweight",
                      "Lightweight",
                      "Featherweight",
                      "Bantamweight",
                      "Flyweight",
                      "Women's Bantamweight",
                      "Women's Flyweight",
                      "Women's Strawweight"]

    # Index for weight_classes
    weight_class = 0

    # Dictionary holding rankings
    rankings = {}

    # This loop stores all rankings in the dictionary
    for table in tables:
        rows = table.find_all("tr")[2:]  # skip header rows
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) >= 6:
                rank = cols[0].get_text(" ", strip=True)
                fighter = cols[2].get_text(" ", strip=True)

                # Removes Wikipedia's tied ranking tag
                if rank[-4:] == " (T)":
                    rank = rank[:-4]

                if rank == "C":
                    rank_string = "(C) "
                else:
                    rank_string = "#" + rank + " "
                rankings[weight_classes[weight_class] + "_" + fighter] = rank_string
        weight_class += 1

    return rankings