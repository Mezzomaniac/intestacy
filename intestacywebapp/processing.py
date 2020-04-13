from intestacywebapp.models import Relative, DescendibleRelative, DeFacto, Estate

def calculate_distribution(
    deathdate, 
    value, 
    specified_items=None, 
    spouse_num=0, 
    spouse='', 
    defactos_num=0, 
    defactos=[], 
    surviving_issue_num=0, 
    surviving_issue=[], 
    nonsurviving_issue_num=0, 
    nonsurviving_issue=[], 
    parents_num=0, 
    parents=[],
    surviving_siblings_num=0, 
    surviving_siblings=[], 
    nonsurviving_siblings_num=0, 
    nonsurviving_siblings=[], 
    grandparents_num=0, 
    grandparents=[],
    surviving_auntuncles_num=0, 
    surviving_auntuncles=[], 
    nonsurviving_auntuncles_num=0, 
    nonsurviving_auntuncles=[]
    ):
    estate = Estate(deathdate, value)
    
    if spouse_num:
        estate.spouse = Relative('Spouse', spouse)
    estate.defactos = [DeFacto(**defacto) for defacto in defactos[:defactos_num]]

    estate.issue = [DescendibleRelative(f'Surviving Child {n}', child) 
        for n, child in enumerate(surviving_issue[:surviving_issue_num], 1)]
    estate.issue.extend(
        DescendibleRelative(f'Non-surviving Child {n}', child['name'], False, 
            [Relative('Grandchild', grandchild) for grandchild in child['issue'][:child['issue_num']]]) 
        for n, child in enumerate(nonsurviving_issue[:nonsurviving_issue_num], 1))

    estate.parents = [Relative('Parent', parent) for parent in parents[:parents_num]]
    
    estate.siblings = [DescendibleRelative(f'Surviving Sibling {n}', sibling) 
        for n, sibling in enumerate(surviving_siblings[:surviving_siblings_num], 1)]
    estate.siblings.extend(
        DescendibleRelative(f'Non-surviving Sibling {n}', sibling['name'], False, 
            [Relative('Niece/Nephew', nibling) for nibling in sibling['issue'][:sibling['issue_num']]]) 
        for n, sibling in enumerate(nonsurviving_siblings[:nonsurviving_siblings_num], 1))

    estate.grandparents = [Relative('Grandparent', grandparent) for grandparent in grandparents[:grandparents_num]]

    estate.auntuncles = [DescendibleRelative(f'Surviving Aunt/Uncle {n}', auntuncle) 
        for n, auntuncle in enumerate(surviving_auntuncles[:surviving_auntuncles_num], 1)]
    estate.auntuncles.extend(
        DescendibleRelative(f'Non-surviving Aunt/Uncle {n}', auntuncle['name'], False, 
            [Relative('Cousin', cousin) for cousin in auntuncle['issue'][:auntuncle['issue_num']]]) 
        for n, auntuncle in enumerate(nonsurviving_auntuncles[:nonsurviving_auntuncles_num], 1))

    estate.distribute()
    return estate