import datetime

ACT_URL = "https://www.legislation.wa.gov.au/legislation/prod/filestore.nsf/FileURL/mrdoc_44687.htm/$FILE/Administration%20Act%201903%20-%20%5B12-d0-00%5D.html#_Toc99367207"
#TODO: Automatically update the Act link when a new version is published

SPECIFIED_ITEMS = {
    datetime.date(1997, 12, 15):
        {'item_2': 50_000,
        'item_3a_and_b': 75_000,
        'item_3bi': 6_000,
        'item_6': 6_000},
    datetime.date(2022, 3, 30):
        {'item_2': 472_000,
        'item_3a_and_b': 705_000,
        'item_3bi': 56_500,
        'item_6': 56_500},
    datetime.date(2023, 8, 2):
        {'item_2': 501_000,
        'item_3a_and_b': 748_500,
        'item_3bi': 60_000,
        'item_6': 60_000},
    datetime.date(2025, 7, 5):
        {'item_2': 546_000,
        'item_3a_and_b': 815_500,
        'item_3bi': 65_500,
        'item_6': 65_500}
    }
# TODO: Automatically check for new orders under s 14A Administration Act

# Acts Amendment (Lesbian and Gay Law Reform) Act 2002 (WA) commencement date:
LG_LAW_REFORM_ACT_02 = datetime.date(2002, 9, 21)

# Family Court Amendment Act 2002 (WA) substantive commencement date:
FAM_CT_AM_ACT_02 = datetime.date(2002, 12, 1)

# Aboriginal Affairs Planning Authority Amendment Act 2012 (WA) commencement date:
AAPA_AM_ACT_12 = datetime.date(2013, 8, 7)
