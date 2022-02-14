from enum import Enum, auto

class EnumExt(Enum):

    def __str__(self) -> str:
        return f'{self.name}'


class Role(EnumExt):

    BANK = auto()
    AGROSMART = auto()
    EDISONAIRPORT = auto()
    MAXWELL = auto()
    NEWSUN = auto()
    VANDERWAALS = auto()
    CLAM = auto()
    NIKOLA = auto()
    WESTERNENERGY = auto()
    BOOGLE = auto()
    FORCE = auto()
    UNION = auto()

    TEST = auto()


class PowerType(EnumExt):

    TOTAL = 0
    GREEN = 1
    FOSSIL = 2
    DEMAND = 3
    

class TransactionType(EnumExt):

    CASH = auto()
    POWER = auto()
    ASSET = auto()
    SMARTAPP = auto()
    SERVICE = auto() 
       
# class Location(EnumExt):

#     LAND = auto()
#     SEA = auto()
#     TIDAL = auto()
#     CITY = auto()

def polishString(string, type_='normal'):

    if type_ == 'normal':
        if string[:1].lower() == 'e':
            return 'EdisonAirport'
        elif string[:2].lower() == 'ne':
            return 'NewSun'
        elif string[:2].lower() == 'sm':
            return 'SmartApp'
        elif string[:1].lower() == 'w':
            return 'WesternEnergy'
        return string[:1].upper() + string[1:].lower()

    elif type_ == 'lower':
        return string.lower()
    elif type_ == 'upper':
        return string.upper()
    else:
        print('Error: Invalid string formatting.')
        return string
    
# print(polishString(PowerType.GREEN.name, 'upper'))
