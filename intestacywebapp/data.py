import datetime

ACT_URL = "https://www.legislation.wa.gov.au/legislation/prod/filestore.nsf/FileURL/mrdoc_44687.htm/$FILE/Administration%20Act%201903%20-%20%5B12-d0-00%5D.html#_Toc99367207"
#TODO: Automatically update the Act link when a new version is published

SPECIFIED_ITEMS = {
    datetime.date(1997, 12, 15):
        {'item_2': 50000,
        'item_3a_and_b': 75000,
        'item_3bi': 6000,
        'item_6': 6000},
    datetime.date(2022, 3, 30):
        {'item_2': 472000,
        'item_3a_and_b': 705000,
        'item_3bi': 56500,
        'item_6': 56500}
    }
# TODO: 21/09/02: parents need not be a mother and father
# TODO: 07/08/13: before this date, Indigenous intestacies are dealt with under the Aboriginal Affairs Planning Authority Act 1972 (WA) instead
# TODO: Automatically check for new orders under s 14A Administration Act

FAM_CT_AM_ACT_02 = datetime.date(2002, 12, 1)
