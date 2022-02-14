import tkinter as tk
from PIL import ImageTk, Image
from abc import ABC, abstractmethod

from pyparsing import col

from enums import Role, TransactionType, polishString
from assets import *
from players import *
from transactions import *

root = tk.Tk()
root.title('Newton Shift - Home')
root.configure(bg='light grey')
 
def sortAssets(assetlist) -> list:
    green_assets = [entry.name for entry in assetlist if entry.power.subtype == PowerType.GREEN]
    green_assets.sort()
    fossil_assets = [entry.name for entry in assetlist if entry.power.subtype == PowerType.FOSSIL]
    fossil_assets.sort() 
    return green_assets + fossil_assets

# refreshing the interface in case of player change or transaction taking place
def refreshInterface(player=p_bank):

    GameElement.emptyWidget(frame_assets)   
    SectionLabel(frame_assets, 'Assets')   

    for idx, asset in enumerate(player.assets):
        asset_label = AssetLabel(frame_assets, asset)
        # decides in which row the element is placed
        if idx < 4:
            asset_label.placeElement(1, idx)
        elif idx < 8:
            asset_label.placeElement(2, idx-4)
        elif idx < 12:
            asset_label.placeElement(3, idx-8)
        else:
            pass

    global power_section
    GameElement.emptyWidget(power_section.frame)    
    power_section = PowerSection(player)
    power_section.placeElement()

    global smart_section
    GameElement.emptyWidget(smart_section.frame)    
    smart_section = SmartAppSection(player)
    smart_section.placeElement()

    GameElement.emptyWidget(frame_services)   
    SectionLabel(frame_services, 'Services') 

    for idx, service in enumerate(player.services):
        service_label = ServiceLabel(frame_services, service)
        # decides in which row the element is placed
        if idx < 4:
            service_label.placeElement(1, idx)
        elif idx < 8:
            service_label.placeElement(2, idx-4)
        else:
            pass


class GameElement(ABC):

    @abstractmethod
    def placeElement() -> None:
        pass
    
    # currently unused. should replace some things in the function that reapplies widgets upon player switch
    def emptyWidget(frame):
        for widget in frame.winfo_children():
                widget.destroy()

# creating a way to map role classes to their enums
player_roles = [player.role.name for player in list_players]
name_to_player = {role: player for role, player in zip(player_roles, list_players)}

class SectionLabel(): 

    def __init__(self, master, section) -> None:
        self.master = master
        self.label = tk.Label(master, text=section, font='Helvetica 18 bold', padx=10, pady=5, borderwidth=2, relief='solid')
        self.label.grid(row=0, column=0, columnspan=5, pady=10)    



class PlayerDropdown(GameElement):

    def __init__(self, master, balance) -> None:  
        self.master = master
        self.balance = balance
        self.role_var = tk.StringVar()
        self.role_var.set('Player')
        self.role_options = [polishString(role.name)for role in Role]
        self.dropdown = tk.OptionMenu(self.master, self.role_var, *self.role_options, command=lambda x: self.changePlayer(self.balance))    
        # https://stackoverflow.com/questions/55621073/add-a-separator-to-an-option-menu-in-python-with-tkinter
        # seperates different playertypes
        self.dropdown['menu'].insert_separator(1)
        self.dropdown['menu'].insert_separator(4)
        self.dropdown['menu'].insert_separator(8)
        self.dropdown['menu'].insert_separator(12)
        self.formatElement()

    # has become very crowded and will be re-structured in a future version
    def changePlayer(self, balance_element):
        player_role = self.role_var.get() 
        selected_player = name_to_player[polishString(player_role, 'upper')]

        refreshInterface(selected_player)

        new_balance = f'$ {str(selected_player.money)}' 
        balance_element.config(text=new_balance)

    def placeElement(self):
        self.dropdown.grid(row=0, column=0, sticky='w')

    def formatElement(self):
        max_width = len(max(self.role_options, key=len))
        # print(max_width)
        self.dropdown.config(width=max_width+1)


class InfoButton(GameElement):

    def __init__(self, master) -> None:
        
        self.master = master
        self.infobutton = tk.Button(
            self.master,
            text='INFO',
            command=self.displayInformation)
        self.formatElement()      

    def displayInformation(self):
        pass        
    
    def formatElement(self):
        self.infobutton.config(padx=20, pady=10)

    def placeElement(self):
        self.infobutton.grid(row=0, column=1, padx=(40,0))


class Balance(GameElement):

    def __init__(self, master):
        self.master = master
        self.amount = tk.Label(
            self.master, 
            text=f'$ ----')
        self.formatElement()
    
    def formatElement(self):
        self.amount.config(font=('Helvetica', 60), fg='green')
        self.amount.config(padx=10)
        self.amount.config(borderwidth=2, relief='solid')

    def placeElement(self):
        self.amount.grid(row=2)


class EnterAmount(GameElement):

    def __init__(self, master):
        self.master = master
        self.amount = tk.Entry(self.master)
        self.formatElement()

    def formatElement(self):
        self.amount.config(width=10, font=('Helvetica', 45))
    
    def placeElement(self):
        self.amount.grid(row=4)


class BuyButton(GameElement):

    def __init__(self, master, partner_radio):  
        self.master = master
        self.partner_radio = partner_radio
        self.buybutton = tk.Button(
            self.master, 
            text='BUY',
            command=self.transfer)
        self.formatElement()
    
    def transfer(self):
        try:
            transaction_volume = int(entrybox.amount.get())
        except ValueError as v:
            # print(v)
            print('Invalid transaction amount entered.')
            transaction_volume = 0
        
        # mapping the options from dropdowns and radio buttons to actual variables
        payer = name_to_player[polishString(player_selection.role_var.get(), 'upper')]      
        receiver_num = playerradio.player_var.get()
        receiver = name_to_player[Role(receiver_num).name]

        transaction = self.chooseTransactionType(transaction_volume, payer, receiver)       
        transaction.performTransaction(transaction.checkViability())

        refreshInterface(payer)
        changeDropdown(playerradio.player_var.get())

        balance.amount.config(text=f'$ {str(payer.money)}')
        entrybox.amount.delete(0, tk.END)

    def chooseTransactionType(self, transaction_volume, payer, receiver):
        # standard transaction
        if typeradio.type_var.get() == TransactionType.STANDARD.value:
            transaction = NormalTransaction(transaction_volume, payer, receiver)
        # asset transaction
        elif typeradio.type_var.get() == TransactionType.ASSET.value:
            # mapping back asset name to asset
            try:
                for asset in receiver.assets:
                    if asset.name == parameters.ass_ser_dropdown.dropdown_var.get():
                        correct_asset = asset                   
            except:
                correct_asset = oil2
                print('base asset was used as dummy for transaction')
            transaction = AssetTransaction(correct_asset, transaction_volume, payer, receiver)
        # smart application transaction
        elif typeradio.type_var.get() == TransactionType.METER.value:           
            transaction = MeterTransaction(parameters.smartapp_var.get(), transaction_volume, payer, receiver)   

        elif typeradio.type_var.get() == TransactionType.SERVICE.value:
            # mapping back service name to service
            try:
                for service in receiver.services:
                    if service.name == parameters.ass_ser_dropdown.dropdown_var.get():
                        correct_service = service                   
            except:
                correct_service = home_ins
                print('base service was used as dummy for transaction')
            transaction = ServiceTransaction(correct_service, transaction_volume, payer, receiver)  

        # power transaction
        elif typeradio.type_var.get() == TransactionType.POWER.value:  
            values = [int(value.get()) if value.get() != '' else 0 for value in parameters.power_entry.boxes]
            for entry in parameters.power_entry.boxes:
                entry.delete(0, tk.END)
            type_ = PowerType.GREEN if parameters.power_entry.energy_type.get() == 'green' else PowerType.FOSSIL
            power = Power(values, subtype=type_)    
            transaction = PowerTransaction(power, transaction_volume, payer, receiver)     

        return transaction
    
    def formatElement(self):
        self.buybutton.config(fg='red')
        self.buybutton.config(padx=30, pady = 20)
    
    def placeElement(self):
        self.buybutton.grid(row=6)


class SpecialTransactionParameters(GameElement):

    def __init__(self) -> None:
        self.master = frame_transactions
        self.frame = tk.Frame(self.master, highlightbackground='green', highlightthickness=2, padx=10, pady=5)
        self.power_entry = PowerEntry(self.frame)

        # for assets
        self.dd_var = tk.StringVar()
        self.dd_var.set('Choose Asset:')
        self.asset_options = [asset.name for asset in p_bank.assets]
        self.ass_ser_dropdown = AssetDropdown(self.frame, p_bank.assets)
        # self.ass_ser_dropdown['menu'].insert_separator(0)

        self.smartapp_var = tk.StringVar()
        self.smartapp_var.set('Chose SmartApp:')
        self.smartapp_options = [polishString(app_name) for app_name in p_bank.smartapps.__dict__.keys()]
        self.smartapp_drowpdown = tk.OptionMenu(self.frame, self.smartapp_var, *self.smartapp_options)      

    def placeElement(self):
        self.frame.grid(row=8, padx=5, pady=5)
        self.ass_ser_dropdown.dropdown.grid(row=0, column=0)
        self.smartapp_drowpdown.grid(row=0, column=1)
        self.power_entry.placeElement()


def changeDropdown(enum_):
    parameters.ass_ser_dropdown.dropdown.destroy()
    player_ = name_to_player[Role(enum_).name]

    if typeradio.type_var.get() == TransactionType.SERVICE.value:
        parameters.ass_ser_dropdown = ServiceDropdown(parameters.frame, player_.services)
    else:  
        parameters.ass_ser_dropdown = AssetDropdown(parameters.frame, player_.assets)           
    parameters.placeElement()

class AssetDropdown(GameElement):

    def __init__(self, master, options, initial_text='Select Asset:') -> None:
        self.master = master
        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set(initial_text)
        # print(options)
        if len(options) < 1:
            self.dropdown_options = ['None']
        else:
            self.dropdown_options = sortAssets(options)
        self.dropdown = tk.OptionMenu(self.master, self.dropdown_var, *self.dropdown_options) 
        separator = sum(asset.power.subtype == PowerType.GREEN for asset in options)
        self.dropdown['menu'].insert_separator(separator)
        self.formatElement()

    def placeElement(self) -> None:
        self.dropdown.grid(row=1, column=2)  

    def formatElement(self) -> None:
        max_width = 15
        self.dropdown.config(width=max_width, bg='GREEN', fg='BLACK')

class ServiceDropdown(GameElement):

    def __init__(self, master, options, initial_text='Select Service:') -> None:
        self.master = master
        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set(initial_text)
        # print(options)
        if len(options) < 1:
            self.dropdown_options = ['None']
        else:
            self.dropdown_options = [opt.name for opt in options]
            self.dropdown_options.sort()
        self.dropdown = tk.OptionMenu(self.master, self.dropdown_var, *self.dropdown_options) 
        self.formatElement()

    def placeElement(self) -> None:
        self.dropdown.grid(row=1, column=2)  

    def formatElement(self) -> None:
        max_width = 15
        self.dropdown.config(width=max_width, bg='#990000', fg='BLACK')


# currently work in progress
class PowerEntry(GameElement):

    def __init__(self, master) -> None:
        self.master = master
        self.frame = tk.Frame(master)
        self.energy = tk.Entry(self.frame)
        self.heating = tk.Entry(self.frame)
        self.mobility = tk.Entry(self.frame)
        self.boxes = [self.energy, self.heating, self.mobility]
        # for radio button
        self.energy_type = tk.StringVar(value='green')
        self.green_button = tk.Radiobutton(self.frame, 
                text='green', 
                variable=self.energy_type, 
                value='green')
        self.fossil_button = tk.Radiobutton(self.frame, 
                text='fossil', 
                variable=self.energy_type, 
                value='fossil')  
        self.widgets = self.boxes + [self.green_button, self.fossil_button]      
        self.formatElement()

    def formatElement(self) -> None:
        self.frame.config(highlightthickness=1, highlightcolor='red')
        for entry in self.boxes:
            entry.config(width=2, justify='center')
    
    def placeElement(self) -> None:
        self.frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.energy.grid(row=0, column=0)
        self.heating.grid(row=0, column=1)
        self.mobility.grid(row=0, column=2)
        self.green_button.grid(row=0, column=3)
        self.fossil_button.grid(row=0, column=4)


class TransactionRadio(GameElement):

    def __init__(self, master) -> None:
        self.master = master
        self.frame = tk.Frame(self.master, highlightbackground='black', highlightthickness=2, padx=10, pady=5)
        self.label = tk.Label(self.frame, text='Transaction Type', borderwidth=1, relief='solid')
        self.radios = list()
        self.type_var = tk.IntVar(value=1)
        self.options = [type_ for type_ in TransactionType]
        for option in self.options:
            radio = tk.Radiobutton(self.frame, 
                text=polishString(option.name), 
                variable=self.type_var, 
                value=option.value, 
                command=disableDistractions)
            self.radios.append(radio)  
        self.formatElement()     
            
    def placeElement(self) -> None:
        self.frame.grid(row=10, padx=10, pady=5)
        self.label.grid(row=0, column=0, sticky='w')

        for idx, radio in enumerate(self.radios[:2]):
            radio.grid(row=idx+1, column=0, sticky='w')       
        for idx, radio in enumerate(self.radios[2:]):
            radio.grid(row=idx, column=1, sticky='w')
    
    def formatElement(self) -> None:
        for widget in self.frame.winfo_children():
            widget.config(padx=5, pady=2)
    
def disableDistractions() -> None:
    if typeradio.type_var.get() == TransactionType.STANDARD.value:
        parameters.ass_ser_dropdown.dropdown.config(state='disabled')
        parameters.smartapp_drowpdown.config(state='disabled')
        for entry_box in parameters.power_entry.widgets:
            entry_box.config(state='disabled')

    elif typeradio.type_var.get() == TransactionType.ASSET.value:
        parameters.ass_ser_dropdown.dropdown.config(state='normal')
        changeDropdown(playerradio.player_var.get())
        parameters.smartapp_drowpdown.config(state='disabled')
        for entry_box in parameters.power_entry.widgets:
            entry_box.config(state='disabled')

    elif typeradio.type_var.get() == TransactionType.METER.value:   
        parameters.ass_ser_dropdown.dropdown.config(state='disabled')
        parameters.smartapp_drowpdown.config(state='normal')
        for entry_box in parameters.power_entry.widgets:
            entry_box.config(state='disabled')

    elif typeradio.type_var.get() == TransactionType.SERVICE.value:
        parameters.ass_ser_dropdown.dropdown.config(state='normal')
        changeDropdown(playerradio.player_var.get())
        parameters.smartapp_drowpdown.config(state='disabled')
        for entry_box in parameters.power_entry.widgets:
            entry_box.config(state='disabled')
            
    elif typeradio.type_var.get() == TransactionType.POWER.value:
        parameters.ass_ser_dropdown.dropdown.config(state='disabled')
        parameters.smartapp_drowpdown.config(state='disabled')
        for entry_box in parameters.power_entry.widgets:
            entry_box.config(state='normal')


class PlayerRadio(GameElement):

    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master, highlightbackground='black', highlightthickness=2, padx=10, pady=5)
        self.player_var = tk.IntVar(value=1)
        self.options = [role for role in Role]
        self.radios = list()
        self.label = tk.Label(self.frame, text='Transaction Partner', borderwidth=1, relief='solid')

        # print(self.options)
        # print(self.player_var)
        for _, option in enumerate(self.options):
            # print(option)
            radio = tk.Radiobutton(self.frame, 
                text=polishString(option.name), 
                variable=self.player_var, 
                value=option.value,
                command=lambda: changeDropdown(self.player_var.get()))
            self.radios.append(radio)

        self.formatElement()

    def placeElement(self):
        self.frame.grid(row=12, padx=10, pady=10)
        self.label.grid(row=0, column=0, sticky='w')
  
        for idx, radio in enumerate(self.radios[:6]):
            radio.grid(row=idx+1, column=0, sticky='w')

        for idx, radio in enumerate(self.radios[6:]):
            radio.grid(row=idx, column=1, sticky='w')
    
    def formatElement(self):
        for widget in self.frame.winfo_children():
            widget.config(padx=5, pady=2)
    

# not fully implemented
class LogWindow(GameElement):

    def __init__(self, master) -> None:
        self.master = master
        self.last_transaction = tk.Label(self.master, text='NONE')
        self.formatElement()

    def placeElement(self)  -> None:
        self.last_transaction.grid(row=14, pady=10)
    
    def formatElement(self) -> None:
        self.last_transaction.config(borderwidth=1, relief='solid')


class PowerSection(GameElement):

    def __init__(self, player) -> None:
        self.frame = tk.Frame(root)
        self.heading = tk.Label(self.frame, text='Power Section', font='Helvetica 18 bold', borderwidth=2, relief='solid', padx=10, pady=10)
        self.green = PowerDisplay(self.frame, player.powerbank.green)
        self.fossil = PowerDisplay(self.frame, player.powerbank.fossil)
        self.demand = PowerDisplay(self.frame, player.powerbank.demand)
        self.total = PowerDisplay(self.frame, player.powerbank.getTotalSupply())
  
    def placeElement(self):
        self.frame.grid(row=0, column=1) 
        self.heading.grid(row=0,column=0, columnspan=2, pady=5)   
        for color, element in zip(['green', 'black', '#990000', 'blue'], [self.green, self.fossil, self.total, self.demand]):
            element.formatElement(color)
        self.green.placeElement(1, 0)
        self.fossil.placeElement(1, 1)
        self.total.placeElement(2, 0, 2)
        self.demand.placeElement(3, 0, 2)


class PowerDisplay(GameElement):

    def __init__(self, master, power: Power):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.text = tk.Label(self.frame, text=power.subtype.name)
        self.label1 = tk.Label(self.frame, text=power.values[0])
        self.label2 = tk.Label(self.frame, text=power.values[1])
        self.label3 = tk.Label(self.frame, text=power.values[2])
    
    def placeElement(self, row: int, column: int, colspan=1):
        self.frame.grid(row=row, column=column, columnspan=colspan, padx=5, pady=5)
        self.text.grid(row=0, columnspan=3)
        self.label1.grid(row=1, column=0)
        self.label2.grid(row=1, column=1)
        self.label3.grid(row=1, column=2)

    def formatElement(self,color):
        self.frame.config(highlightthickness=2, highlightbackground=color)

current_year = 1

class SmartAppSection(GameElement):

    def __init__(self, player):
        self.master = root
        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.subframe = tk.Frame(self.frame)
        self.new_year_button = tk.Button(self.subframe, text='Year '+str(current_year+1), padx=20, pady=10, command=self.newYearClick)
        self.stats = tk.Button(self.subframe, text='Stats', padx=20, pady=10)
        self.quit_ = QuitButton(self.subframe)
        self.appdisplay = SmartAppDisplay(self.frame, player)

    def placeElement(self):
        self.frame.grid(row=0, column=2)
        self.subframe.pack()
        self.new_year_button.grid(row=0, column=0)
        self.stats.grid(row=0, column=1)
        self.quit_.placeElement()
        self.appdisplay.placeElement()

    def newYearClick(self):
        new_year_number = int(self.new_year_button.cget('text')[-1])
        for player in list_players:
            player.newYear(new_year_number)

        global current_year
        current_year +=1
        current_player = name_to_player[polishString(player_selection.role_var.get(), 'upper')]
        refreshInterface(current_player)
        balance.amount.config(text=f'$ {str(current_player.money)}')
      

class SmartAppDisplay(GameElement):

    def __init__(self, master, player) -> None:
        self.master = master
        self.frame = tk.Frame(self.master)
        self.grid_display = OneSmartApp(self.frame, player, 'grid', 'red')
        self.meter_display = OneSmartApp(self.frame, player, 'meter', 'green')
        self.storage_display = OneSmartApp(self.frame, player, 'storage', 'blue')

    def placeElement(self):
        self.frame.pack()
        self.grid_display.placeElement(0)
        self.meter_display.placeElement(1)
        self.storage_display.placeElement(2)


class OneSmartApp(GameElement):

    def __init__(self, master, player, name: str, color: str) -> None:
        self.master = master
        self.frame = tk.Frame(self.master)
        self.name = tk.Label(self.frame, text=name)
        self.icon = tk.Label(self.frame, text=color)
        self.color = color

        if player.smartapps.__dict__[name] <= 0:
            status_text = 'INACTIVE'
            text_color = 'grey'
        else:
            status_text = 'ACTIVE'
            text_color = 'orange'

        self.status = tk.Label(self.frame, text=status_text, fg=text_color)
        self.formatElement()

    
    def placeElement(self, number):

        self.frame.grid(row=0, column=number) 
        for widget in [self.name, self.icon, self.status]:
            widget.pack()

    def formatElement(self):
        self.icon.config(fg=self.color)


class QuitButton(GameElement):

    def __init__(self, master):
        self.master = master
        self.quitbutton = tk.Button(
            self.master, text='QUIT', 
            command=self.close, 
            padx=20, 
            pady=10)
        self.formatElement()

    def close(self):
        root.destroy()     

    def placeElement(self):
        self.quitbutton.grid(row=0, column=2)

    def formatElement(self):
        self.quitbutton.config(fg='red')


class AssetLabel(GameElement):

    def __init__(self, master, asset) -> None:

        if len(asset.name) > 8:
            text = asset.name
            index = text.find(' ')
            text = text[:index] + '\n' + text[index+1:]
        else:
            text = asset.name

        self.master = master
        self.asset = asset
        self.container = tk.Frame(self.master)
        self.name_label =  tk.Label(self.container, text=text)
        self.power_type = tk.Label(self.container, text=self.asset.power.subtype.name)
        self.power_values = tk.Label(self.container, text=f'{self.asset.power.values}')
        self.formatElement()

    def placeElement(self, row, column):
        self.container.grid(row=row, column=column, padx=5, pady=5)
        self.name_label.pack()
        self.power_type.pack()
        self.power_values.pack()

    def formatElement(self):
        if self.asset.power.subtype == PowerType.GREEN:
            color = 'green'
            text_col = 'black'
        else:
            color = 'black'
            text_col = 'white'
        self.container.config(highlightbackground=color, highlightthickness=2)
        self.name_label.config(fg=text_col, bg=color)
        self.power_type.config(fg=color)  

class ServiceLabel(GameElement):

    # basically copy of asset label, will be improved in the future
    def __init__(self, master, service) -> None:

        if len(service.name) > 8:
            text = service.name
            index = text.find(' ')
            text = text[:index] + '\n' + text[index+1:]
        else:
            text = service.name

        self.master = master
        self.service = service
        self.container = tk.Frame(self.master)
        self.name_label =  tk.Label(self.container, text=text)
        self.power_type = tk.Label(self.container, text=self.service.power.subtype.name)
        self.power_values = tk.Label(self.container, text=f'{self.service.power.values}')
        self.formatElement()

    def placeElement(self, row, column):
        self.container.grid(row=row, column=column, padx=5, pady=5)
        self.name_label.pack()
        self.power_type.pack()
        self.power_values.pack()

    def formatElement(self):
        color = '#990000'
        self.container.config(highlightbackground=color, highlightthickness=2)
        self.name_label.config(bg=color, fg='white')
        self.power_type.config(fg=color)  


class ErrorWindow():

    def __init__(self, master) -> None:
        self.master = master
     
# do all the frames
#####################
frame_transactions = tk.Frame(root)
frame_power = tk.Frame(root, padx=150, pady=70)
frame_assets = tk.Frame(root, padx=50, pady=30)
frame_services = tk.Frame(root, padx=50, pady=30)

frame_transactions.grid(row=0, column=0, rowspan=2)
frame_power.grid(row=0, column=1)
frame_assets.grid(row=1, column=1)
frame_services.grid(row=1, column=2)
######################


# do everything in transaction screen
transaction_subframe = tk.Frame(frame_transactions, padx=20, pady=10)
transaction_subframe.grid(sticky='w')

# player drop down is dependent of the balance, so balance has to be created first
balance = Balance(frame_transactions)
balance.placeElement()

player_selection = PlayerDropdown(transaction_subframe, balance.amount)
player_selection.placeElement()
info_button = InfoButton(transaction_subframe)
info_button.placeElement()

entrybox = EnterAmount(frame_transactions)
entrybox.placeElement()
typeradio = TransactionRadio(frame_transactions)
playerradio = PlayerRadio(frame_transactions)
buy = BuyButton(frame_transactions, playerradio)
buy.placeElement()

parameters = SpecialTransactionParameters()
parameters.placeElement()

typeradio.placeElement()
playerradio.placeElement()

# log_window = LogWindow()


# other stuff

asset_section_label = tk.Label(frame_assets, text='Assets', font='Helvetica 18 bold', padx=10, pady=5, borderwidth=2, relief='solid')
asset_section_label.grid(row=0, column=0, columnspan=2)

# populate power frame

power_section = PowerSection(p_bank)
power_section.placeElement()

smart_section = SmartAppSection(p_bank)
smart_section.placeElement()

service_label = SectionLabel(frame_services, 'Services')

# test = ServiceDropdown(root, p_bank.services)
# test.dropdown.grid(row=0,column=5)

root.mainloop()

