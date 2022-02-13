from enums import PowerType

class Power():

    # power costs are used to facilitate power transactions between players. not yet implemented
    energy_cost = 70
    heating_cost = 50
    mobility_cost = 90
    
    def __init__(self, values=[0,0,0], subtype=PowerType.GREEN):

        self.values = values
        self.subtype = subtype

    def __str__(self):
        return f'Type: {self.subtype.name} -- {self.values}'
    
    def changePower(self, power_dif):
        self.values = [old + new for old, new in zip(self.values, power_dif.values)]

# templates:
green_power = Power()
fossil_power = Power(subtype=PowerType.FOSSIL)
total_power = Power(subtype=PowerType.TOTAL)

# testing changePower() method. changes one Power object in accordances to another
test_power = Power([2,3,1])
green_power.changePower(test_power)


# this combines information about the power status of each player
class PowerBank():
        
    def __init__(self):
        self.green = Power()
        self.fossil = Power(subtype=PowerType.FOSSIL)
        self.demand = Power(subtype=PowerType.DEMAND, values=[5,5,5])

    def getTotalSupply(self):
        total_energy = [g + b for g, b in zip(self.green.values, self.fossil.values)]
        return Power(total_energy, subtype=PowerType.TOTAL)
        
        
class Asset:

    def __init__(self, name: str, cost: int, power, central=True):
        self.name = name
        self.cost = cost
        self.power = power
        self.central = central

    def __repr__(self):
        return f'Asset("{self.name}", {self.cost}, {self.power.values[0]}, {self.power.values[1]}, {self.power.values[2]}, {self.power.subtype}, {self.central})'

    def __str__(self):
        return f'{self.name} -- Cost: {self.cost} -- Supply: {self.power.values} -- Green Energy: {self.power.subtype}'
    
    def __eq__(self, other):
        return self.name == other.name

        
class Service():
    # quant: 5

    def __init__(self, name: str, cost: int, power):
        self.name = name
        self.cost = cost
        self.power = power
        # Service.quant -= 1

    def __repr__(self) -> str:
        return f'Service("{self.name}", "{self.cost}", {self.power.values[0]}, {self.power.values[1]}, {self.power.values[2]})'

    def __str__(self) -> str:
        return f'{self.name} -- Cost: {self.cost} -- Changes: {self.power.values}'

# similar to the PowerBank, this contains all information about Smart Applications for each player
class SmartAppsOverview():

    def __init__(self, grid=0, meter=0, storage=0):
        self.grid = grid
        self.meter = meter
        self.storage = storage

    def __str__(self) -> str:
        return f'Grids: {self.grid} -- Meters: {self.meter} -- Storage: {self.storage}'

    def changeCount(self, type_: str, amount: int):

        type_ = type_.lower()
        
        if type_ == 'grid':
            self.grid += amount
            
        elif type_ == 'meter':
            self.meter += amount
            
        elif type_ == 'storage':
            self.storage += amount


# creation of all assets
# the three numbers after the cost are for energy, heating, mobility

# the bank has most assets prior to purchase
bankassets = list()

gas1 = Asset('Gas 1', 2250, Power(subtype=PowerType.FOSSIL, values=[5,5,5]))
gas2 = Asset('Gas 2', 3000, Power(subtype=PowerType.FOSSIL, values=[10,10,10]))
coal1 = Asset('Coal 1', 2400, Power(subtype=PowerType.FOSSIL, values=[8,8,0]))

oil2 = Asset('Oil 2', 3000, Power(subtype=PowerType.FOSSIL, values=[10,10,10]))

solar1 = Asset('Solar 1', 800, Power(values=[8, 0, 0]), central=False)
geothermal = Asset('Building Geothermal', 1800, Power(values=[0, 6, 0]), central=False)
blwind = Asset('Bladeless Wind', 1800, Power(values=[0, 0, 5]), central=False)
solarpv = Asset('Building Integrated PV', 900, Power(values=[6, 0, 0]), central=False)


# print(gas1)

# powerbank = PowerBank()
# print(powerbank.getTotalSupply())

# powerbank.green.changePower(test_power)
# print(powerbank.green)
# print(powerbank.getTotalSupply())

# gas1 = Asset('Gas 1', 2250, 5, 5, 5, )
# gas2 = Asset('Gas 2', 3000, 10, 10, 10, )
# oil1 = Asset('Oil 1', 2250, 5, 5, 5, )
# oil2 = Asset('Oil 2', 3000, 10, 10, 10, )
# coal1 = Asset('Coal 1', 2400, 8, 8, 0, )
# coal2 = Asset('Coal 2', 2400, 12, 12, 0, )
# shgas1 = Asset('Shale Gas 1', 2400, 0, 12, 0, )
# shgas2 = Asset('Shale Gas 2', 3000, 0, 20, 0, )

# bankassets += [gas1, gas2, oil1, oil2, coal1, coal2, shgas1, shgas2] * 2

# wind1 = Asset('Wind 1', 1200, 8, 0, 0, green_central)
# wind2 = Asset('Wind 2', 1800, 12, 0, 0, green_central)
# wind3 = Asset('Wind 3', 2400, 16, 0, 0, green_central)
# wind4 = Asset('Wind 4', 2000, 20, 0, 0, green_central)

# bankassets += [wind1, wind2, wind3, wind4] * 2

# # sort by names of the assets
# bankassets.sort(key = lambda x: x.name)

# # for asset in bankassets: print(asset)

# solar1 = Asset('Solar 1', 800, 8, 0, 0, green_central)
# solar2 = Asset('Solar 2', 1800, 12, 0, 0, green_central)
# solar3 = Asset('Solar 3', 1500, 10, 0, 0, green_central)
# tidal1 = Asset('Tidal 1', 800, 4, 0, 0, green_central)
# tidal2 = Asset('Solar 1', 2000, 8, 0, 0, green_central)
# hydrcell1 = Asset('Hydrogen Fuel Cell 1', 4800, 0, 0, 16, green_central)
# hydrcell2 = Asset('Hydrogen Fuel Cell 1', 4800, 8, 0, 24, green_central)
# nuclear = Asset('Nuclear', 6500, 18, 8, 0, green_central)
# nuclearfus = Asset('Nuclear Fusion', 6000, 20, 0, 0, green_central)
# tachyongen = Asset('Tachyon Generator', 7500, 10, 10, 10, green_central)

# blwind = Asset('Bladeless Wind', 1800, 0, 0, 5, green_decentral)
# geothermal = Asset('Building Geothermal', 1800, 0, 6, 0, green_decentral)
# heatpump = Asset('Heatpump', 3200, 0, 8, 0, green_decentral)
# solarpv = Asset('Building Integrated PV', 900, 6, 0, 0, green_decentral)
# quantumgen = Asset('Quantum Generator', 15000, 10, 10, 10, green_decentral)



home_ins = Service('Home Insulation', 1000, Power(subtype=PowerType.DEMAND, values=[-4,-4,0]))
app_lease = Service('Lease of Appliances', 2000, Power(subtype=PowerType.DEMAND, values=[-4,-4,0]))
# placeholder cost for drone_delivery
drone_delivery = Service('Drone Delivery', 1000, Power(subtype=PowerType.DEMAND, values=[6,0,-2]))
electric_mob = Service('Electric Mobility', 2000, Power(subtype=PowerType.DEMAND, values=[5,0,-5]))
business_eff = Service('Business Efficiency', 3000, Power(subtype=PowerType.DEMAND, values=[-4,-4,-4]))
# print(home_ins)

inventory = SmartAppsOverview()

# print(inventory)
# inventory.changeCount('Grid', 1)
# print(inventory)

