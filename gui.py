import tkinter as tk
from PIL import ImageTk, Image
from abc import ABC, abstractmethod

from enums import Role, TransactionType, polishString
from assets import Power #, PowerBank, Asset, Service, SmartAppsOverview
from players import *
from transactions import CashTransaction, PowerTransaction, SmartAppTransaction, AssetTransaction, ServiceTransaction

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

    # Power Section
    global power_section
    GameElement.emptyWidget(power_section.frame)    
    power_section = PowerSection(player)
    power_section.placeElement()

    # Smart Application Section
    global smart_section
    GameElement.emptyWidget(smart_section.frame)    
    smart_section = SmartAppSection(player)
    smart_section.placeElement()

    # Asset Section
    GameElement.emptyWidget(frame_assets)   
    SectionLabel(frame_assets, 'Assets')   
    for idx, asset in enumerate(player.assets):
        asset_label = AssetLabel(frame_assets, asset)
        # decides in which row the element is placed
        if idx < 4:
            asset_label.placeElement(1, idx)
        elif idx < 8:
            asset_label.placeElement(2, idx-4)
        else:
            pass
    
    # Service Section
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


class SectionLabel(): 

    def __init__(self, master, section) -> None:
        self.master = master
        self.label = tk.Label(master, text=section, font='Helvetica 18 bold', padx=10, pady=10, borderwidth=2, relief='solid')
        self.label.grid(row=0, column=0, columnspan=5, pady=10)    


class GameElement(ABC):

    @abstractmethod
    def placeElement() -> None:
        pass
    
    def emptyWidget(frame):
        for widget in frame.winfo_children():
                widget.destroy()

# creating a way to map role classes to their enums
player_roles = [player.role.name for player in list_players]
name_to_player = {role: player for role, player in zip(player_roles, list_players)}


class PlayerDropdown(GameElement):

    def __init__(self, master, balance) -> None:  
        self.master = master
        self.balance = balance
        self.role_var = tk.StringVar()
        self.role_var.set('Player')
        self.role_options = [polishString(role.name)for role in Role]
        self.dropdown = tk.OptionMenu(self.master, self.role_var, *self.role_options, command=lambda x: self.changePlayer(self.balance))    
        # hard codes separator between players into the dropdown menu
        for position in [1, 4, 8, 12]:
            self.dropdown['menu'].insert_separator(position)
        self.formatElement()

    def changePlayer(self, balance_element):
        player_role = self.role_var.get() 
        selected_player = name_to_player[polishString(player_role, 'upper')]
        refreshInterface(selected_player)
        # refreshes the balance
        new_balance = f'$ {str(selected_player.money)}' 
        balance_element.config(text=new_balance)

    def placeElement(self):
        self.dropdown.grid(row=0, column=0, sticky='w')

    def formatElement(self):
        max_width = len(max(self.role_options, key=len))
        self.dropdown.config(width=max_width+1)

# currently no use implemented
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
        self.amount.config(font=('Helvetica', 60), fg='green', padx=10)
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
        # CASH transaction
        if typeradio.type_var.get() == TransactionType.CASH.value:
            transaction = CashTransaction(transaction_volume, payer, receiver)
       
        # Smart Application Transaction
        elif typeradio.type_var.get() == TransactionType.SMARTAPP.value:           
            transaction = SmartAppTransaction(parameters.purchase_dropdown.dropdown_var.get(), transaction_volume, payer, receiver)   
            print(parameters.purchase_dropdown.dropdown_var.get())

        # ASSET Transaction
        elif typeradio.type_var.get() == TransactionType.ASSET.value:
            # mapping back asset name to asset
            try:
                for asset in receiver.assets:
                    if asset.name == parameters.purchase_dropdown.dropdown_var.get():
                        correct_asset = asset                   
            except:
                correct_asset = oil2
                print('base asset was used as dummy for transaction')
            transaction = AssetTransaction(correct_asset, transaction_volume, payer, receiver)

        # SERVICE Transaction
        elif typeradio.type_var.get() == TransactionType.SERVICE.value:
            # mapping back service name to service
            try:
                for service in receiver.services:
                    if service.name == parameters.purchase_dropdown.dropdown_var.get():
                        correct_service = service                   
            except:
                correct_service = home_ins
                print('base service was used as dummy for transaction')
            transaction = ServiceTransaction(correct_service, transaction_volume, payer, receiver)  

        # POWER Transaction
        elif typeradio.type_var.get() == TransactionType.POWER.value:  
            values = [int(value.get()) if value.get() != '' else 0 for value in parameters.power_entry.boxes]
            for entry in parameters.power_entry.boxes:
                entry.delete(0, tk.END)
            type_ = PowerType.GREEN if parameters.power_entry.energy_type.get() == 'green' else PowerType.FOSSIL
            power = Power(values, subtype=type_)    
            transaction = PowerTransaction(power, transaction_volume, payer, receiver)     

        return transaction
    
    def formatElement(self):
        self.buybutton.config(fg='red', font=('Times New Roman bold', 30))
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
        self.purchase_dropdown = AssetDropdown(self.frame, p_bank.assets)

    def placeElement(self):
        self.frame.grid(row=8, padx=5, pady=5)
        self.purchase_dropdown.dropdown.grid(row=0, column=0)
        self.power_entry.placeElement()

# switch content of the dropdown to contain either assets, services or smartapps
def changeDropdown(enum_):
    parameters.purchase_dropdown.dropdown.destroy()
    player_ = name_to_player[Role(enum_).name]

    if typeradio.type_var.get() == TransactionType.SERVICE.value:
        parameters.purchase_dropdown = ServiceDropdown(parameters.frame, player_.services)
    elif typeradio.type_var.get() == TransactionType.SMARTAPP.value:
        parameters.purchase_dropdown = SmartAppDropdown(parameters.frame, player_)
    else:  
        parameters.purchase_dropdown = AssetDropdown(parameters.frame, player_.assets)           
    parameters.placeElement()

    if typeradio.type_var.get() == TransactionType.CASH.value or typeradio.type_var.get() == TransactionType.POWER.value:
        parameters.purchase_dropdown.dropdown.config(state='disabled')
    else:
        parameters.purchase_dropdown.dropdown.config(state='normal')
    
    
# next three classes should be merged into one eventually
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

class SmartAppDropdown(GameElement):

    def __init__(self, master, player, initial_text='Select SmartApp:') -> None:
        self.master = master
        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set(initial_text)
        # print(options)
        self.dropdown_options = [polishString(app_name) for app_name in player.smartapps.__dict__.keys()]
        self.dropdown = tk.OptionMenu(self.master, self.dropdown_var, *self.dropdown_options) 
        self.formatElement()

    def placeElement(self) -> None:
        self.dropdown.grid(row=1, column=2)  

    def formatElement(self) -> None:
        max_width = 15
        self.dropdown.config(width=max_width, bg='#000099', fg='BLACK')



# Entry and RadioButton to fetch values for power amount and type
class PowerEntry(GameElement):

    def __init__(self, master) -> None:
        self.master = master
        self.frame = tk.Frame(master)
        # power images
        self.img_energy = Icon(self.frame, size=25, image='energy.png')
        self.img_heat = Icon(self.frame, size=25, image='heat.png')
        self.img_mobility = Icon(self.frame, size=25, image='mobility.png') 
        self.images = [self.img_energy, self.img_heat, self.img_mobility] 
        # power entry boxes
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
        for entry in self.boxes:
            entry.config(width=2, justify='center')
    
    def placeElement(self) -> None:
        self.frame.grid(row=1, column=0, columnspan=2, pady=5)
        for idx, img in enumerate(self.images):
            img.grid(row=0, column=idx)
        for idx, entry in enumerate(self.boxes):
            entry.grid(row=1, column=idx)
        self.green_button.grid(row=0, column=3)
        self.fossil_button.grid(row=1, column=3)


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

def switchPowerEntry(state='disabled') -> None:
    for entry_box in parameters.power_entry.widgets:
            entry_box.config(state=state)
    
def disableDistractions() -> None:
    if typeradio.type_var.get() == TransactionType.CASH.value:
        parameters.purchase_dropdown.dropdown.config(state='disabled')
        switchPowerEntry()

    elif (typeradio.type_var.get() == TransactionType.ASSET.value):
        parameters.purchase_dropdown.dropdown.config(state='normal')
        changeDropdown(playerradio.player_var.get())
        switchPowerEntry()

    elif typeradio.type_var.get() == TransactionType.SMARTAPP.value:   
        parameters.purchase_dropdown.dropdown.config(state='normal')
        changeDropdown(playerradio.player_var.get())
        switchPowerEntry()

    elif typeradio.type_var.get() == TransactionType.SERVICE.value:
        parameters.purchase_dropdown.dropdown.config(state='normal')
        changeDropdown(playerradio.player_var.get())
        switchPowerEntry()
            
    elif typeradio.type_var.get() == TransactionType.POWER.value:
        parameters.purchase_dropdown.dropdown.config(state='disabled')
        switchPowerEntry('normal')


class PlayerRadio(GameElement):

    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master, highlightbackground='black', highlightthickness=2, padx=10, pady=5)
        self.player_var = tk.IntVar(value=1)
        self.options = [role for role in Role]
        self.radios = list()
        self.label = tk.Label(self.frame, text='Transaction Partner', borderwidth=1, relief='solid')

        for _, option in enumerate(self.options):
            radio = tk.Radiobutton(self.frame, 
                text=polishString(option.name), 
                variable=self.player_var, 
                value=option.value,
                command=lambda: changeDropdown(self.player_var.get()))
            self.radios.append(radio)

        self.formatElement()

    def placeElement(self):
        self.frame.grid(row=12, padx=10, pady=5)
        self.label.grid(row=0, column=0, sticky='w')
  
        for idx, radio in enumerate(self.radios[:6]):
            radio.grid(row=idx+1, column=0, sticky='w')

        for idx, radio in enumerate(self.radios[6:]):
            radio.grid(row=idx, column=1, sticky='w')
    
    def formatElement(self):
        for widget in self.frame.winfo_children():
            widget.config(padx=5, pady=2)
    

# not implemented yet
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
        self.frame = tk.Frame(root, padx=20, pady=10)
        # self.heading = tk.Label(self.frame, text='Power Section', font='Helvetica 18 bold', borderwidth=2, relief='solid', padx=10, pady=10)
        self.heading = SectionLabel(self.frame, 'Power Section')
        self.green = PowerDisplay(self.frame, player.powerbank.green)
        self.fossil = PowerDisplay(self.frame, player.powerbank.fossil)
        self.demand = PowerDisplay(self.frame, player.powerbank.demand)
        self.total = PowerDisplay(self.frame, player.powerbank.getTotalSupply())
  
    def placeElement(self):
        self.frame.grid(row=0, column=1) 
        self.heading.label.grid(row=0,column=0, columnspan=2, pady=5)   
        for color, element in zip(['green', 'black', '#990000', 'blue'], [self.green, self.fossil, self.total, self.demand]):
            element.formatElement(color)
        self.green.placeElement(1, 0)
        self.fossil.placeElement(1, 1)
        self.total.placeElement(2, 0, colspan=2)
        self.demand.placeElement(3, 0, colspan=2)


class PowerDisplay(GameElement):

    def __init__(self, master, power: Power):
        self.master = master
        self.frame = tk.Frame(self.master, padx=5)
        self.text = tk.Label(self.frame, text=power.subtype.name)
        # places image and power values for each power type
        for num, img in enumerate(['energy.png', 'heat.png', 'mobility.png']):
            image = Icon(self.frame, image=img)
            image.grid(row=1, column=num)
            power_value = tk.Label(self.frame, text=power.values[num], font='Helvetica 17',padx=5)
            power_value.grid(row=2, column=num, padx=5, pady=5)
    
    def placeElement(self, row: int, column: int, colspan=1):
        self.frame.grid(row=row, column=column, columnspan=colspan, padx=5, pady=5)
        self.text.grid(row=0, columnspan=3, pady=8)

    def formatElement(self,color):
        self.frame.config(highlightthickness=2, highlightbackground=color)
        self.text.config(font='Helvetica 14 bold')

# prevents garbage collection of image. source: https://stackoverflow.com/questions/58788728/in-tkinter-is-this-a-good-way-of-avoiding-unwanted-garbage-collection
class Icon(tk.Label):
    def __init__(self, parent, size=20, **kwargs):
        self.image = Image.open(kwargs['image'])
        self._image = ImageTk.PhotoImage(self.image.resize((size, size), Image.ANTIALIAS))

        kwargs['image'] = self._image
        super().__init__(parent, **kwargs)

current_year = 1

class SmartAppSection(GameElement):

    def __init__(self, player):
        self.master = root
        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.heading = SectionLabel(self.frame, 'Smart Applications')
        self.subframe = tk.Frame(self.frame)
        self.new_year_button = tk.Button(self.subframe, text='Year '+str(current_year+1), padx=20, pady=10, command=self.newYearClick)
        self.stats = tk.Button(self.subframe, text='Stats', padx=20, pady=10)
        self.quit_ = QuitButton(self.subframe)
        self.appdisplay = SmartAppDisplay(self.frame, player)

    def placeElement(self):
        self.frame.grid(row=0, column=2)
        self.subframe.grid(row=1, column=0, columnspan=2)
        self.new_year_button.grid(row=1, column=0)
        self.stats.grid(row=1, column=1)
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
        self.grid_display = OneSmartApp(self.frame, player, 'grid', 'grid.png','red')
        self.meter_display = OneSmartApp(self.frame, player, 'meter', 'meter.png', 'green')
        self.storage_display = OneSmartApp(self.frame, player, 'storage', 'storage.png', 'blue')

    def placeElement(self):
        self.frame.grid(row=2, column=0, columnspan=3)
        self.grid_display.placeElement(0)
        self.meter_display.placeElement(1)
        self.storage_display.placeElement(2)


class OneSmartApp(GameElement):

    def __init__(self, master, player, name: str, image: str, color: str) -> None:
        self.master = master
        self.frame = tk.Frame(self.master)
        self.name = tk.Label(self.frame, text=name)
        self.icon = tk.Label(self.frame, text=color)
        self.color = color
        self.image = Icon(self.frame, size=70, image=image)

        if player.smartapps.__dict__[name] <= 0:
            status_text = 'INACTIVE'
            text_color = 'grey'
        else:
            status_text = 'ACTIVE'
            text_color = 'orange'

        self.status = tk.Label(self.frame, text=status_text, fg=text_color, font=('Helvetica 14 bold'))
        self.formatElement()

    
    def placeElement(self, number):

        self.frame.grid(row=0, column=number) 
        for widget in [self.image, self.status]:
            widget.pack(pady=5)

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
        self.quitbutton.grid(row=1, column=2)

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
     

# frame_power = tk.Frame(root, padx=150, pady=70)
# frame_power.grid(row=0, column=1)



# do everything in transaction screen
frame_transactions = tk.Frame(root)
frame_transactions.grid(row=0, column=0, rowspan=2)

# has to be created ahead of player drowdown because of dependency
balance = Balance(frame_transactions)

# top row of transaction section
transaction_subframe = tk.Frame(frame_transactions, padx=20, pady=10)
transaction_subframe.grid(sticky='w')
player_selection = PlayerDropdown(transaction_subframe, balance.amount)
player_selection.placeElement()
info_button = InfoButton(transaction_subframe)
info_button.placeElement()

# place the rest of transaction windwow
balance.placeElement()
entrybox = EnterAmount(frame_transactions)
entrybox.placeElement()
typeradio = TransactionRadio(frame_transactions)
playerradio = PlayerRadio(frame_transactions)
# depends on playerradio, therefore the order
buy = BuyButton(frame_transactions, playerradio)
buy.placeElement()

parameters = SpecialTransactionParameters()
typeradio.placeElement()
playerradio.placeElement()
parameters.placeElement()



# frame_transactions = tk.Frame(root)
# frame_transactions.grid(row=0, column=0, rowspan=2)

# # has to be created ahead of player drowdown because of dependency
# balance = Balance(frame_transactions)

# # top row of transaction section
# transaction_subframe = tk.Frame(frame_transactions, padx=20, pady=10)
# transaction_subframe.grid(sticky='w')
# player_selection = PlayerDropdown(transaction_subframe, balance.amount)
# player_selection.placeElement()
# info_button = InfoButton(transaction_subframe)
# info_button.placeElement()

# # place the rest of transaction windwow
# balance.placeElement()
# entrybox = EnterAmount(frame_transactions)
# entrybox.placeElement()
# typeradio = TransactionRadio(frame_transactions)
# playerradio = PlayerRadio(frame_transactions)
# # depends on playerradio, therefore the order
# buy = BuyButton(frame_transactions, playerradio)
# buy.placeElement()

# parameters = SpecialTransactionParameters()
# parameters.placeElement()
# typeradio.placeElement()
# playerradio.placeElement()


# populate power frame
power_section = PowerSection(p_bank)
power_section.placeElement()

# populate SmartSection frame
smart_section = SmartAppSection(p_bank)
smart_section.placeElement()

# create Assset Section (frame not included in class)
frame_assets = tk.Frame(root, padx=50, pady=30)
frame_assets.grid(row=1, column=1)
asset_section_label = SectionLabel(frame_assets, 'Assets')

# create Service Section (frame not included in class)
frame_services = tk.Frame(root, padx=50, pady=30)
frame_services.grid(row=1, column=2)
service_label = SectionLabel(frame_services, 'Services')

disableDistractions()
# testing images

# photo_label = PhotoImageLabel(root, image='energy.png')
# photo_label.grid(row=4, column=4)

root.mainloop()

