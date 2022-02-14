from assets import *
from enums import Role


# define the base class for all players
class Player:

    # counter for total number of players
    playercount = 0
    allplayers = list()

    # information to be updated whenever a new in-game year begins
    demandUpdate = {1: [5, 5, 5], 2: [8, 8, 8], 3: [10, 10, 10], 4: [16, 16, 16]}
    fundsUpdate = {1: 1000, 2: 2000, 3: 3000, 4: 4000}

    role = Role.TEST
    
    def __init__(self):

        self.money = 3000
        self.assets = list()
        self.services = list()
        self.smartapps = SmartAppsOverview()
        self.powerbank = PowerBank()

        Player.playercount += 1
        Player.allplayers.append(self.role)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __str__(self):
        return f'Player: {self.role}'

    def initializeSupply(self):

        for asset in self.assets:
            if asset.power.subtype == PowerType.GREEN:
                self.powerbank.green.values = [old+new for old, new in zip(asset.power.values, self.powerbank.green.values)]
            else:
                self.powerbank.fossil.values = [old+new for old, new in zip(asset.power.values, self.powerbank.fossil.values)]

    def listAssets(self):

        if len(self.assets) == 0:
            print('No assets owned.')
            return

        print('----'*10)

        print('Owned assets:')
        for asset in self.assets:
            print(f'* {asset}')
        
        print('----'*10)

    def listSmartApps(self):
        print(self.smartapps)
       
    def listServices(self):
        print('Services:')
        for serv in self.services:
            print(serv)

    def newYear(self, year: int):
        self.powerbank.demand = Power(subtype=PowerType.DEMAND, values=self.demandUpdate[year])
        self.money += self.fundsUpdate[year]


class Bank(Player):
    fundsUpdate = {1: 1000000, 2: 0, 3: 0, 4: 0}
    demandUpdate = {1: [0, 0, 0], 2: [0, 0, 0], 3: [0, 0, 0], 4: [0, 0, 0]}

    role = Role.BANK

    def __init__(self):
        super().__init__()
        self.money = 1337
        self.powerbank.demand.values = [0, 0, 0]
        # current selection of assets and services is a placeholder
        self.assets = [gas1, gas2, coal1, oil2, solar1, geothermal, blwind, solarpv]*2
        self.services = [home_ins, app_lease, drone_delivery, electric_mob, business_eff]*2
     
# define properties for energy companies
class EnergyComp(Player):

    fundsUpdate = {1: 3000, 2: 0, 3: 0, 4: 0}
    demandUpdate = {1: [0, 0, 0], 2: [0, 0, 0], 3: [0, 0, 0], 4: [0, 0, 0]}

    def __init__(self):
        super().__init__()
        self.money = 3000
        self.powerbank.demand.values = [0, 0, 0]


class Clam(EnergyComp):

    role = Role.CLAM

    def __init__(self):
        super().__init__()
        self.assets = [oil2, coal1]


class Nikola(EnergyComp):

    role = Role.NIKOLA

    def __init__(self):
        super().__init__()
        self.assets = [solar1]


class WesternEnergy(EnergyComp):

    fundsUpdate = {1: 2000, 2: 0, 3: 0, 4: 0}

    role = Role.WESTERNENERGY

    def __init__(self):
        super().__init__()
        self.money = 2000
        self.assets = [gas2]

# define properties shared by AgroSmart and Edison Airport
class Company(Player):

    fundsUpdate = {1: 1200, 2: 1800, 3: 2250, 4: 3600}

    def __init__(self):
        super().__init__()
        self.money = 1200


class AgroSmart(Company):

    role = Role.AGROSMART 

    def __init__(self):
        super().__init__()
        self.assets = [geothermal]


class Airport(Company):

    role = Role.EDISONAIRPORT


# define properties for people/communities
class People(Player):
    pass


class Maxwell(People):
    
    fundsUpdate = {1: 1500, 2: 2400, 3: 3000, 4: 4800}

    role = Role.MAXWELL

    def __init__(self):
        super().__init__()
        self.money = 1500
        self.assets = [blwind]
    

class SunSociety(People):
    
    fundsUpdate = {1: 1200, 2: 1800, 3: 2700, 4: 3600}

    role = Role.NEWSUN

    def __init__(self):
        super().__init__()
        self.money = 1200
        self.assets = [solarpv]


class Vanderwall(People):
    
    fundsUpdate = {1: 750, 2: 1200, 3: 1500, 4: 2400}

    role = Role.VANDERWAALS

    def __init__(self):
        super().__init__()
        self.money = 750

# special class Boogle
class Boogle(Player):

    fundsUpdate = {1: 1500, 2: 2400, 3: 3000, 4: 4600}

    role = Role.BOOGLE

    def __init__(self):
        super().__init__()
        self.money = 750
        self.smartapps.grid = 1
        self.smartapps.meter = 1
        self.smartapps.storage = 1
        

# special class The Force Investments
class Force(Player):
    
    fundsUpdate = {1: 5000, 2: 5000, 3: 5000, 4: 5000}

    role = Role.FORCE

    def __init__(self):
        super().__init__()
        self.money = 5000
        self.powerbank.demand.values = [0, 0, 0]


# special class The Union
class Union(Player):

    fundsUpdate = {1: 3000, 2: 3000, 3: 3000, 4: 3000}

    role = Role.UNION

    def __init__(self):
        super().__init__()
        self.money = 3000
        self.powerbank.demand.values = [0, 0, 0]


## creating one instance for each player/role
p_test = Player()

p_bank = Bank()

p_clam = Clam()
p_nikola = Nikola()
p_west_en = WesternEnergy()

p_agrosmart = AgroSmart()
p_edisonair = Airport()

p_maxwell = Maxwell()
p_sunsociety = SunSociety()
p_vanderwall = Vanderwall()

p_boogle = Boogle()
p_force = Force()
p_union = Union()

list_players =   [
            p_bank, p_test,
            p_clam, p_nikola, p_west_en, 
            p_agrosmart, p_edisonair, 
            p_maxwell, p_sunsociety, p_vanderwall, 
            p_boogle, p_force, p_union]

for player in list_players:
    player.initializeSupply()

# print(p_bank.smartapps.__dict__)
# print(Player.allplayers)
# print(Player.playercount)


# for player in Player:
#     print(player)

# print(Player.playercount)
# p_agrosmart.newYear(3)
# print(p_agrosmart)
# p_boogle.listSmartApps()
# p_clam.listAssets()
# p_union.listServices()
# print(Player.allplayers)

# p_clam.initializeSupply()
# print(p_clam.powerbank.fossil)
# print(p_clam.powerbank.getTotalSupply())

## doesn't work yet

# listing Inventory should state the player name