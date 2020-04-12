try:
    from intestacywebapp.models import *
except ImportError:
    from models import *

estate = Estate(datetime.date.today(), Decimal('1234567.89'))
estate.spouse = Relative('Spouse', 'Wifey')
estate.defactos = [DeFacto(name='Angela', length=5), DeFacto(name='Pamela', length=2), DeFacto(name='Sandra', length=0), DeFacto(name='Rita', length=2)]
estate.parents = [Relative('Parent', 'Mum'), Relative('Parent', 'Dad')]
estate.siblings = [DescendibleRelative('Surviving Sibling 1', 'Little Bro'), DescendibleRelative('Surviving Sibling 2', 'Little Sis')]
estate.siblings.append(DescendibleRelative('Non-surviving Sibling 1', 'Big Bro', False, [Relative('Niece', 'Dog'), Relative('Nephew', 'Cat'), Relative('Niece', 'Fish')]))
estate.siblings.append(DescendibleRelative('Non-surviving Sibling 2', 'Big Sis', False, [Relative('Nephew', 'Monkey'), Relative('Niece', 'Dolphin'), Relative('Nephew', 'Lion')]))
estate.distribute()