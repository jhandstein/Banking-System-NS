from abc import ABC, abstractmethod
from enums import polishString
from players import *



# transaction base class
class Transaction(ABC):

    def __init__(self, amount: int, payer: Player, receiver=p_bank):
        self.amount = amount
        self.payer = payer
        self.receiver = receiver

    @abstractmethod
    # must return True for transaction to take place
    def checkViability(self):
        # only allow transaction if funds are sufficient
        if self.payer.money >= self.amount:
            if self.amount > 0:
                return True       
            else:
                print('Entered 0 or negative number') 
                return False   
        else:
            print('Insufficient funds!')
            return False
    
    @abstractmethod
    def performTransaction(self, check):  
        # only performs transaction if it is viable    
        if check == False:
            print("Couldn't perform transaction!")
            return False

        print(f'{polishString(self.payer.role.name)} payed {self.amount} to {polishString(self.receiver.role.name)}')
        self.payer.money -= self.amount
        self.receiver.money += self.amount

        # this line makes sure that children of Transaction() can add to the requirements of performTransaction
        return True

            
class NormalTransaction(Transaction):   

    def checkViability(self):
        if super().checkViability() is False:
            return False
        else:
            print('Transaction is viable')
            return True

    def performTransaction(self, check):
        super().performTransaction(check)


class AssetTransaction(Transaction):

    def __init__(self, asset, amount, payer, receiver=p_bank):
        super().__init__(amount, payer, receiver=receiver)
        self.asset = asset

    def checkViability(self):

        if super().checkViability() is False:
            return False

        if not self.asset in self.receiver.assets:
            print('This asset is not for sale!')
            return False
        
        print('Viable for purchase')
        return True
      
    
    def performTransaction(self, check):

        if super().performTransaction(check) == True:
            self.receiver.assets.remove(self.asset)
            self.payer.assets.append(self.asset)

            neg_power = Power(values=[-num for num in self.asset.power.values])

            if self.asset.power.subtype == PowerType.GREEN:
                self.receiver.powerbank.green.changePower(neg_power) 
                self.payer.powerbank.green.changePower(self.asset.power)   
                 
            else:
                self.receiver.powerbank.fossil.changePower(neg_power)  
                self.payer.powerbank.fossil.changePower(self.asset.power)                 

        else:
            print('No assets were traded!')


class MeterTransaction(Transaction):
    
    
    def __init__(self, app: str, amount, payer, receiver=p_bank):
        super().__init__(amount, payer, receiver=receiver)
        self.app = app.lower()

    def checkViability(self):

        if super().checkViability() is False:
            return False

        # smartapps.__dict__ returns a dictionary with all values of smartapps
        if self.receiver.smartapps.__dict__[self.app] <= 0:
            print(f'No smart {self.app} for sale!')
            return False
        
        print('Viable for purchase!')
        return True
    
    def performTransaction(self, check):
        if super().performTransaction(check) == True:            

            self.receiver.smartapps.changeCount(self.app, -1)
            self.payer.smartapps.changeCount(self.app, 1)
            
        else:
            print('No meters traded!')

        
class ServiceTransaction(Transaction):

    def __init__(self, service, amount, payer, receiver=p_bank):
        super().__init__(amount, payer, receiver=receiver)
        self.service = service

    def checkViability(self):
        if super().checkViability() is False:
            return False
        
        if not self.service in self.receiver.services:
            print('This service is not for sale!')          
            return False
        
        print('Viable for purchase!')
        return True

    def performTransaction(self, check):
        if super().performTransaction(check) == True:
            self.receiver.services.remove(self.service)
            self.payer.services.append(self.service)

            # adjust energy of player here
            neg_energy = Power(values=[-num for num in self.service.power.values])

            self.receiver.powerbank.demand.changePower(neg_energy)
            self.payer.powerbank.demand.changePower(self.service.power)


            print(f'Traded: {self.service}')
        
        else:
            print('No service was traded.')


class PowerTransaction(Transaction):

    def __init__(self, power, amount, payer, receiver=p_bank):
        super().__init__(amount, payer, receiver=receiver)
        self.power = power

    def compareEnergyValues(self):

        if self.power.subtype == PowerType.GREEN:
            power_receiver = self.receiver.powerbank.green
        
        elif self.power.subtype == PowerType.FOSSIL:
            power_receiver = self.receiver.powerbank.fossil
        
        for a,b in zip(self.power.values, power_receiver.values):
            if a < 0:
                    print("Can't sell negative power.")
                    return False
            if a > b:
                    print('Insufficient Energy for Transaction.')
                    return False
    
    def checkViability(self):
        if super().checkViability() is False:
            return False
        
        if self.compareEnergyValues() is False:
            return False

        print('Viable for purchase!')
        return True

    def performTransaction(self, check):
        if super().performTransaction(check) == True:

            if self.power.subtype == PowerType.GREEN:
                power_receiver = self.payer.powerbank.green
                power_donor = self.receiver.powerbank.green
        
            elif self.power.subtype == PowerType.FOSSIL:
                power_receiver = self.payer.powerbank.fossil
                power_donor = self.receiver.powerbank.fossil

            power_receiver.changePower(self.power)

            neg_energy = Power(values=[-num for num in self.power.values])
            power_donor.changePower(neg_energy)

            print(f'Traded: {self.power}')
        
        else:
            print('No power was traded.')

# test = PowerTransaction(test_power, 300, p_clam)

# test.performTransaction(test.checkViability())
##

# power_transfer = PowerTransaction(Power(values=[3,1,0], subtype=PowerType.FOSSIL), 100, p_edisonair, receiver=p_clam)
# huch = power_transfer.checkViability()
# power_transfer.performTransaction(huch)

# new_power_transfer = PowerTransaction(Power(values=[5,0,0], subtype=PowerType.FOSSIL), 100, p_edisonair, receiver=p_clam)
# new_power_transfer.compareEnergyValues()

# p_energy_test = Player()
# p_energy_test.powerbank.green.values = [10,10,10]

# print(p_energy_test.powerbank.green)

# green_power_trans = PowerTransaction(Power(values=[100,0,0], subtype=PowerType.GREEN), 100, p_agrosmart, receiver=p_energy_test)
# green_power_trans.performTransaction(green_power_trans.checkViability())

# print(p_energy_test.powerbank.green)
# print(p_agrosmart.powerbank.green)

# test1 = NormalTransaction(300, p_agrosmart)
# test2 = NormalTransaction(30000, p_agrosmart)
# test3 = AssetTransaction(coal1, 500, p_edisonair, p_clam)
# test4 = AssetTransaction(coal1, 500, p_sunsociety, p_bank)
# test_service = ServiceTransaction(home_ins, 500, p_agrosmart)


# p_clam.initializeSupply()
# test3.performTransaction(test3.checkViability())

# p_clam.listAssets()
# p_edisonair.listAssets()

# print(p_clam.powerbank.getTotalSupply(), p_edisonair.powerbank.getTotalSupply())
# p_bank.listServices()

# test_service.performTransaction(test_service.checkViability())

# p_clam.listServices()
# p_bank.listServices()

# print(p_agrosmart.powerbank.demand, p_bank.powerbank.demand)


# perform a test transaction
# return_value = test2.checkViability()
# test2.performTransaction(return_value)

# for idx, trans in enumerate([test1, test2, test3, test4]):

#     print(f'*Test {idx+1}:')
#     return_value = trans.checkViability()
#     # print(return_value)
#     trans.performTransaction(return_value)

#     print(trans.payer, trans.payer.assets)

# service = Service('Home Insulation', 1000, -4, -4, 0)

# p_bank.services = [service]

# trade_service = ServiceTransaction(service, 300, p_test)

# x = trade_service.checkViability()
# trade_service.performTransaction(x)

# meters = MeterTransaction('grid', 300, p_test)
# # meters = MeterTransaction('grid', 100, p_test, p_boogle)
# x = meters.checkViability()
# meters.performTransaction(x)

# print(p_test.smartapps)

