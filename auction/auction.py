import streamlit as st
import pandas as pd
import json
import os
import random
import datetime
import numpy as np
from PIL import ImageDraw,Image,ExifTags,ImageOps
# import yaml
from dotenv import load_dotenv


load_dotenv()

# Constants
# Configurable parameters
MIN_BID_PRICE = int(os.getenv("MIN_BID_PRICE",0))
MAX_BID_PRICE = int(os.getenv("MAX_BID_PRICE",40000))
TOTAL_PURSE_VALUE = int(os.getenv("TOTAL_PURSE_VALUE", 1000000))
MAX_PLAYERS_PER_TEAM = int(os.getenv("MAX_PLAYERS_PER_TEAM",9))

# Dont edit the below constants
MASTER_DF_CSV = 'masterdf.csv'
PLAYERS_DATA_JSON = 'players_data.json'
SOLD_PLAYERS_DIR = 'sold_players'
UNSOLD_PLAYERS_DIR = 'unsold_players'
ENROLLED_PLAYERS_DIR = '.\\enrolled_players\\'
TEAMS_DIR = 'teams'
WALLET_DF_CSV=f".\\{TEAMS_DIR}\\wallet.csv"
SOLD_DF_CSV = f".\\{TEAMS_DIR}\\sold_players.csv"
CAPTAINS_CSV = 'captains.csv'
DEFAULT_IMAGE = ".\\default_image.jpg"



# Styling for Sidebar buttons
st.markdown("""<style>[data-testid=stSidebar] {background-color: #DFFFFF; color: blue;}</style>""", unsafe_allow_html=True)

# Create necessary directories
def makedir(name):
    if not os.path.exists(name):
        os.makedirs(name)
        print("Created new folder =", name)
makedir(SOLD_PLAYERS_DIR)
makedir(UNSOLD_PLAYERS_DIR)
makedir(TEAMS_DIR)

def get_date():
    d=str(datetime.datetime.now())
    date_string=d.split(" ")[0] +'_' +d.split(" ")[1].split('.')[0]
    return date_string

# Create master dataframe/csv to capture all auction activities 
if not os.path.isfile(MASTER_DF_CSV):
    master_columns = ['date', 'captain', 'player', 'status', 'price', 'phone', 'wing']
    pd.DataFrame(columns=master_columns).to_csv(MASTER_DF_CSV, index=False)

# Load captain data purse value, number of players
captaindf = pd.read_csv(CAPTAINS_CSV)
order_names = sorted(captaindf['name'].tolist())
captain_names = ['None'] + order_names


# Get the list of all players and dump them into a json file
st.session_state.players_data={}
for player in os.listdir(path=ENROLLED_PLAYERS_DIR):
    player_list=player.split('_')
    player_list.append(player)
    st.session_state.players_data[player_list[0]]=player_list[1:]  
# Convert and write JSON object to file
with open(PLAYERS_DATA_JSON, "w") as outfile: 
    json.dump(st.session_state.players_data, outfile)

# Function to get the new player randomly
def get_new_player():
    with open(PLAYERS_DATA_JSON) as json_file:
        players_data = json.load(json_file)
    enrolled_players= list(players_data.keys())

    masterdf = pd.read_csv(MASTER_DF_CSV)
    auctioned_players_list = masterdf['player'].unique()
    try:
        player_for_auction=random.choice(list(set(enrolled_players) - set(auctioned_players_list)))
        print("Player for auction = ",player_for_auction,players_data[player_for_auction])
        return player_for_auction,players_data[player_for_auction]
    except:
        st.warning("All Players are Auctioned.Click on EXIT button.",icon="⚠️")
        st.session_state.exit_button_enabled = True
        st.session_state.price_input = st.session_state.widget
        st.session_state.widget = ""
        st.session_state.selection_reset = 'None'
        st.session_state.fetch_button_enabled=False  
        return False, False

def display_default_image():
    st.session_state.image_url= DEFAULT_IMAGE
    st.session_state.sell_message =""
    st.session_state.player_name ="Player Name"
    st.session_state.player_style = "Playing Style" 

# Function Definitions for Button Actions
def fetch_data():
    print("Fetching new player for aution.")
    player_for_auction,player_metadata=get_new_player()
    if player_for_auction and player_metadata :
        st.session_state.player_name = player_for_auction
        st.session_state.player_wing = player_metadata[0]
        st.session_state.player_ph = player_metadata[1]
        st.session_state.player_style = player_metadata[2].split(".")[0]
        
        st.session_state.image_url = ENROLLED_PLAYERS_DIR + player_metadata[-1]
        st.session_state.df = pd.DataFrame(columns=captain_names[1:],index=range(MAX_PLAYERS_PER_TEAM))

        # Reset the previous BID price and captain selection values before new fetching of the players
        st.session_state.price_input = st.session_state.widget
        st.session_state.widget = ""
        st.session_state.selection_reset = 'None'
        st.session_state.sell_message =" "

        # Enable the sell and unsold buttons after fetching data
        st.session_state.buttons_enabled = True
        # Reset button clicks (to allow them to be clicked again after fetching new data)
        st.session_state.sell_button_clicked = False
        st.session_state.unsold_button_clicked = False
        
        pending_count= str((len(list(st.session_state.players_data.keys())) - (int(st.session_state.players_sold_count)+int(st.session_state.players_unsold_count))))
        print("Remaining players for auction =",pending_count)
        if pending_count==0:
            st.session_state.exit_button_enabled=True
    else:
        # When all players are auctioned display the default image 
        display_default_image()

def sell_player():
    # disable sold and unsold button ater clicking once
    st.session_state.sell_button_clicked = True
    st.session_state.unsold_button_clicked = True

    if not (st.session_state.captain_choice =='None' or st.session_state.price_input ==''):
        # # create player records for book keeping
        player_sell_record = [ get_date(),st.session_state.captain_choice,
                                st.session_state.player_name,'sold',st.session_state.price_input,
                                st.session_state.player_ph,st.session_state.player_wing ]
        masterdf = pd.read_csv(MASTER_DF_CSV) 
        # # Check wallet if player can be sold to a the captain
        current_wallet_balance=TOTAL_PURSE_VALUE-masterdf[masterdf['captain']==st.session_state.captain_choice]['price'].sum()
        captain_wallet_player_count =masterdf[masterdf['captain']==st.session_state.captain_choice]['player'].count()

        try:
            wallet_max_purchase_price =int(masterdf[masterdf['captain']==st.session_state.captain_choice]['price'].max())
        except:
            wallet_max_purchase_price = 0

        has_captain_used_max_bid_price_condition = (wallet_max_purchase_price == MAX_BID_PRICE) and (st.session_state.price_input == MAX_BID_PRICE)

        ## Bid price should not exceed the captain's wallet balance and the balance should be sufficient to purchase the remaining players needed to complete the team
        min_balance_required_for_remaining_players = ((MAX_PLAYERS_PER_TEAM - captain_wallet_player_count) * MIN_BID_PRICE)

        print("Current balance =",current_wallet_balance,
              "Current player count =",captain_wallet_player_count,
              "Current max purchase price=",wallet_max_purchase_price,
              "Min balance maintain=",min_balance_required_for_remaining_players)

        st.session_state.sell_condition = True
        # Conditions to sell a player to the captain
        if (int(st.session_state.price_input) >= MIN_BID_PRICE and int(st.session_state.price_input) <= MAX_BID_PRICE):
            if ((MAX_PLAYERS_PER_TEAM -captain_wallet_player_count) == 1) or (captain_wallet_player_count == 0):
                print("Dont check after bid remaining balance condition")
            else:
                print("Check after bid remaining balance condition")
                
                future_balance=current_wallet_balance - int(st.session_state.price_input)
                future_players_count=captain_wallet_player_count+1
                future_min_balance_required_for_remaining_players = ((MAX_PLAYERS_PER_TEAM - future_players_count) * MIN_BID_PRICE)

                print("current_wallet_balance=",current_wallet_balance,\
                      "current players count=",captain_wallet_player_count,\
                      "current remaining players to buy=",MAX_PLAYERS_PER_TEAM-captain_wallet_player_count,\
                      "current min balance maintain=",min_balance_required_for_remaining_players,\
                      "future_balance=",future_balance,\
                      "future players count=",future_players_count,\
                      "future remaining players to buy=",MAX_PLAYERS_PER_TEAM-future_players_count,\
                      "future min balance maintain=",future_min_balance_required_for_remaining_players)
                
                if not future_balance >= future_min_balance_required_for_remaining_players:
                    print("Bid price is not sufficient to purchase remaining players")
                    st.session_state.sell_condition = False
                    # future_balance=current_wallet_balance - int(st.session_state.price_input)
                    error_msg= f"Current balance = {int(current_wallet_balance)} and player count ={captain_wallet_player_count}.\
                                After the bid price of {int(st.session_state.price_input)} \
                                your balance would be {int(future_balance)} and players count would be {future_players_count}.\
                                To complete the team, a minimum balance of {int(future_min_balance_required_for_remaining_players)} \
                                would be required to buy the remaining {MAX_PLAYERS_PER_TEAM-future_players_count} players @{MIN_BID_PRICE} per player."    
                                

                    # error_msg =f"After this Bid price your balance would be {int(future_balance)}.\
                    #             Minimum purse of {future_min_balance_required_for_remaining_players},will be needed to purchase remaining \
                    #                 {MAX_PLAYERS_PER_TEAM-future_players_count} players @{MIN_BID_PRICE} per player."
        else:
            st.session_state.sell_condition = False
            error_msg = f"Bid price should be between {MIN_BID_PRICE} and {MAX_BID_PRICE}."
            print(error_msg)
        if st.session_state.sell_condition:
            print(f"Captain wallet={st.session_state.captain_choice},\
                  bal={current_wallet_balance},\
                    total spent={TOTAL_PURSE_VALUE-current_wallet_balance},\
                        player= {captain_wallet_player_count}")
            masterdf.loc[len(masterdf.index)] = list(player_sell_record)
            masterdf.to_csv(MASTER_DF_CSV,index=False)
            st.session_state.players_sold_count = str(masterdf[masterdf['status']=='sold']['status'].count())
            st.session_state.sell_message = f"Sold to {st.session_state.captain_choice} for {st.session_state.price_input}"
            total_sold_player_count=masterdf[masterdf['status']=='sold'].shape[0]
            if total_sold_player_count == MAX_PLAYERS_PER_TEAM*len(order_names):
                st.session_state.exit_button_enabled=True
                st.session_state.fetch_button_enabled=False
                st.warning("All Players are Auctioned. Click on EXIT button to wrap up auction.")

            # Update Wallet Table after selling player
            masterdf.replace(to_replace='None', value=np.nan,inplace=True)
            masterdf.fillna(0, inplace=True)
            masterdf['price']=masterdf['price'].astype(int,errors='ignore') 
            row_id=st.session_state.walletdf.loc[st.session_state.walletdf['captain']==st.session_state.captain_choice].index[0]
            price_value = masterdf[masterdf['captain']==st.session_state.captain_choice]['price'].sum()
            player_count_value=masterdf[masterdf['captain']==st.session_state.captain_choice]['player'].count()
            st.session_state.walletdf.loc[row_id,'total spent']=price_value
            st.session_state.walletdf.loc[row_id,'player']=player_count_value
            st.session_state.walletdf.loc[row_id,'balance']=TOTAL_PURSE_VALUE-price_value
            with open(PLAYERS_DATA_JSON) as json_file:
                players_data = json.load(json_file)
            if  len(players_data.keys())==  len(masterdf['player'].unique()):
                st.session_state.exit_button_enabled=True
            print("Player sell record = ",player_sell_record)
        else:
            print("Player purchase not approved.")       
            msg = f"Wallet balance price ={current_wallet_balance} and purchased players ={captain_wallet_player_count}"
            print("Error message =",error_msg)
            st.session_state.sell_message=f"Sale not approved to {st.session_state.captain_choice}.\n{error_msg}"
            st.session_state.sell_button_clicked = False
            st.session_state.unsold_button_clicked = False
            st.session_state.wallet_exceeded_captains.append(st.session_state.captain_choice)
    else:
        st.session_state.sell_message="Something went wrong.\nPlease check BID price and CAPTAIN name.If issue persists, clear cache and re-run/reload the webpage."
        st.session_state.buttons_enabled =True
        st.session_state.sell_button_clicked =False   


def unsold_player():
    # disable sold and unsold button ater clicking once
    st.session_state.sell_button_clicked = True
    st.session_state.unsold_button_clicked = True   
    # create player records for book keeping
    player_unsell_record = [ get_date(),'None',
                            st.session_state.player_name,'unsold','None',
                            str(st.session_state.player_ph),st.session_state.player_wing ]
    
    st.session_state.sell_message = f"SORRY , NO BUYERS !!!"
    masterdf = pd.read_csv(MASTER_DF_CSV) 
    masterdf.loc[len(masterdf.index)] = list(player_unsell_record)
    masterdf.to_csv(MASTER_DF_CSV,index=False)
    st.session_state.players_unsold_count = str(masterdf[masterdf['status']=='unsold']['status'].count())

    with open(PLAYERS_DATA_JSON) as json_file:
        players_data = json.load(json_file)
    if  len(players_data.keys())==  len(masterdf['player'].unique()):
        st.session_state.exit_button_enabled=True
    print("Player unsold record=",player_unsell_record)

def exit_auction():
    # # Move sold and unsold players to separate folders
    print("Clicked on exit button")
    st.session_state.image_url= DEFAULT_IMAGE 
    st.session_state.player_name =""
    st.session_state.player_style = "" 
    st.session_state.sell_message =""
    # st.session_state.emoji =""      
    masterdf = pd.read_csv(MASTER_DF_CSV) 
    with open(PLAYERS_DATA_JSON) as json_file:
        players_data = json.load(json_file)
    sold_players=list(masterdf[masterdf['status']=='sold']['player'])
    unsold_players=list(masterdf[masterdf['status']=='unsold']['player'])
    unauctioned_players=list(set(players_data.keys()).difference(set(sold_players).union(set(unsold_players))))

    # add unauction player to the master df
    for player in unauctioned_players:
        unauction_record= [get_date(),'None',player,'unauction',np.nan,str(players_data[player][1]),players_data[player][0]]
        masterdf.loc[masterdf.shape[0]]=unauction_record
    masterdf.to_csv(MASTER_DF_CSV,index=False)
    # print("Sold players" ,len(sold_players),sold_players) 
    # print("Unsold players",len(unsold_players),unsold_players) 
    # print("Unauctioned players",len(unauctioned_players),unauctioned_players) 
    if len(players_data.keys())>0:       
        for sold in sold_players:
            image_to_move=players_data[sold][-1]
            source = ENROLLED_PLAYERS_DIR+image_to_move
            destination=f".\\{SOLD_PLAYERS_DIR}\\{image_to_move}" 
            os.rename(source, destination)                         
        for unsold in unsold_players:
            image_to_move=players_data[unsold][-1]
            source = ENROLLED_PLAYERS_DIR+image_to_move
            destination=f".\\{UNSOLD_PLAYERS_DIR}\\{image_to_move}" 
            os.rename(source, destination)      
        for unauction in unauctioned_players:
            image_to_move=players_data[unauction][-1]
            source = ENROLLED_PLAYERS_DIR+image_to_move
            destination=f".\\{UNSOLD_PLAYERS_DIR}\\{image_to_move}"   
            os.rename(source, destination)

    st.session_state.exit_button_clicked = True
    # Reset the previous BID price and captain selection values before new fetching of the players
    st.session_state.price_input = st.session_state.widget
    st.session_state.widget = ""
    st.session_state.selection_reset = 'None'
    st.session_state.fetch_button_enabled=False

    # create separate csv files for each captain with his team
    masterdf['captain'].fillna('None',inplace=True)
    for captain in list(set(masterdf['captain'].values)):
        file_name = "unsold_players.csv" if captain == 'None' else f"{captain}'s_team.csv"
        print("Creating teams =",file_name)
        file_path = f".\\{TEAMS_DIR}\\{file_name}"
        masterdf[masterdf['captain']==captain].reset_index(drop=True).to_csv(file_path)
    # creating the final wallet table in the end
    st.session_state.walletdf.reset_index(drop=True).to_csv(WALLET_DF_CSV)
    # creating final sold table in the end
    masterdf = pd.read_csv(MASTER_DF_CSV)
    solddf=masterdf[masterdf['status']=='sold'][['captain','player']]
    data={}
    for cap in solddf['captain'].unique():
        data[cap]=solddf[solddf['captain']==cap]['player'].to_list()
    pd.DataFrame(data=data).reset_index(drop=True).to_csv(SOLD_DF_CSV)


# def crop_image(image):
#     print("Cropping the image")  
#     image = Image.open(image)
#     new_image = image.resize((1280, 853))
#     return new_image

def resize_image(image, width, height):
    image_thumbnail = image.copy()
    image_thumbnail.thumbnail((width, height))
    return image_thumbnail
      
def potrait_image_orientation(image):
    orientation_corrected =False
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())
        if exif[orientation] == 3:
            image=image.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6:
            image=image.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8:
            image=image.transpose(Image.ROTATE_90)
        # print("Image orientation is corrected =",image.size)
        orientation_corrected=True
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    return image,orientation_corrected

def get_max_price_spent_per_player(temp_wallet_df):
    masterdf = pd.read_csv(MASTER_DF_CSV)
    for captain_choice in temp_wallet_df['captain'].unique():
        if type(captain_choice)== str:
            max_price=(masterdf[masterdf['captain']==captain_choice]['price'].max())
        else:
            max_price=0        
        temp_wallet_df.loc[temp_wallet_df['captain']==captain_choice,'max spent per player']=max_price
    return temp_wallet_df

def get_min_balance_required_max_price_spent_per_player(temp_wallet_df):
    masterdf = pd.read_csv(MASTER_DF_CSV)
    for captain_choice in temp_wallet_df['captain'].unique():
        if type(captain_choice)== str:
            max_price=(masterdf[masterdf['captain']==captain_choice]['price'].max())
            currentplayer_count=(masterdf[masterdf['captain']==captain_choice]['player'].count())
            if currentplayer_count == MAX_PLAYERS_PER_TEAM:
                min_balance = 0
            else:   
                min_balance = (MAX_PLAYERS_PER_TEAM - currentplayer_count) * MIN_BID_PRICE
        else:
            max_price=0       
        temp_wallet_df.loc[temp_wallet_df['captain']==captain_choice,'max spent per player']=max_price
        temp_wallet_df.loc[temp_wallet_df['captain']==captain_choice,'min balance required']=min_balance
    return temp_wallet_df


# Initialize session state for dynamic elements
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=captain_names[1:],index=range(MAX_PLAYERS_PER_TEAM))
if 'unsolddf' not in st.session_state:
    masterdf = pd.read_csv(MASTER_DF_CSV)  
    st.session_state.unsolddf =masterdf[(masterdf['status']=='unsold') | (masterdf['status']=='unauction')][['date', 'player', 'phone', 'wing']].reset_index(drop=True)
if 'walletdf' not in st.session_state:
    if masterdf.empty:
        walletdf = pd.DataFrame(data={'captain':captain_names[1:]})
        walletdf[['balance']]=[TOTAL_PURSE_VALUE]
        walletdf[['max spent per player']]=[0]
        walletdf[['total spent']]=[0]
        walletdf[['player']]=[0]
        st.session_state.walletdf = walletdf
    else:
        df1=masterdf[['captain','price']].groupby(['captain']).sum()['price'].to_frame().reset_index().sort_values(by='captain')
        df2=masterdf[['captain','player']].groupby(['captain']).count()['player'].to_frame().reset_index().sort_values(by='captain')
        walletdf=df1.merge(df2,how='inner', on='captain')
        walletdf['balance'] = TOTAL_PURSE_VALUE - walletdf['price']
        walletdf.rename(columns={'price':'total spent'},inplace=True)
        walletdf=walletdf[['captain', 'balance','total spent', 'player']]
        name_diff=list(set(captain_names[1:])-set(walletdf['captain'].values))
        df3 = pd.DataFrame(data={'captain':name_diff})
        df3[['balance']]=[TOTAL_PURSE_VALUE]
        df3[['total spent']]=[0]
        df3[['player']]=[0]

        st.session_state.walletdf=pd.concat([walletdf,df3])
if 'players_sold_count' not in st.session_state:
    masterdf = pd.read_csv(MASTER_DF_CSV)  
    st.session_state.players_sold_count = str(masterdf[masterdf['status']=='sold']['status'].count())
if 'players_unsold_count' not in st.session_state:
    st.session_state.players_unsold_count = str(masterdf[masterdf['status']=='unsold']['status'].count())
if 'players_data' not in st.session_state:
    st.session_state.players_data={}    
if 'auction_pending_count' not in st.session_state:
    st.session_state.auction_pending_count = str((len(list(st.session_state.players_data.keys())) - (int(st.session_state.players_sold_count)+int(st.session_state.players_unsold_count))))   
if 'image_url' not in st.session_state:
    # Set default image (dummy image) when the app first loads
    st.session_state.image_url = DEFAULT_IMAGE 
if 'player_name' not in st.session_state:
    st.session_state.player_name = "Player Name"
if 'player_style' not in st.session_state:
    st.session_state.player_style = "Playing Style"    
if 'price_input'  not in st.session_state:
    st.session_state.price_input = ''
if 'buttons_enabled' not in st.session_state:
    # Initially, the buttons are disabled
    st.session_state.buttons_enabled = False    
if 'sell_button_clicked' not in st.session_state:
    # Track if the SELL button has been clicked
    st.session_state.sell_button_clicked = False
if 'unsold_button_clicked' not in st.session_state:
    # Track if the UNSOLD button has been clicked
    st.session_state.unsold_button_clicked = False
if 'exit_button_enabled' not in st.session_state:
    st.session_state.exit_button_enabled = False
if 'exit_button_clicked' not in st.session_state:
    st.session_state.exit_button_clicked = False    
if 'fetch_button_enabled' not in st.session_state:
    st.session_state.fetch_button_enabled = True
if "sell_message" not in st.session_state:
    st.session_state.sell_message =" "
if 'sell_condition' not in st.session_state:
    st.session_state.sell_condition = True
if 'wallet_exceeded_captains' not in st.session_state:
    st.session_state.wallet_exceeded_captains = []
if 'log_df' not in st.session_state:
    st.session_state.log_df = pd.read_csv(MASTER_DF_CSV)      

# Sidebar with containers
with st.sidebar:
    # Container 1: FETCH button
    with st.container(border=True):
        fetch_button = st.button('**FETCH NEW PLAYER**', on_click=fetch_data,use_container_width=True,disabled=not st.session_state.fetch_button_enabled)  
    # Container 2: Bid price, Captain name, and SELL button
    with st.container(border=True):
        price_col, captain_col,sell_col = st.columns(3)
        with price_col:
            st.session_state.price_input = st.text_input('BIDDING PRICE',value='',placeholder="$$$$", key="widget")
        with captain_col:
            masterdf = pd.read_csv(MASTER_DF_CSV)      
            df=masterdf[['captain','player']].groupby(['captain']).count().reset_index()
            captain_drop_down_list=list(df[df['player']==MAX_PLAYERS_PER_TEAM]['captain'].values)
            captain_drop_down_list= list(set(captain_names)-(set(captain_drop_down_list)))
            captain_drop_down_list.remove('None')
            captain_drop_down_list.sort()
            captain_drop_down_list=['None']+captain_drop_down_list
            st.session_state.captain_choice = st.selectbox(label ='CAPTAIN NAME', options=captain_drop_down_list,key="selection_reset")
        with sell_col:
            st.session_state.sell_button = st.button('**SELL PLAYER**',on_click=sell_player,disabled=not st.session_state.buttons_enabled or st.session_state.sell_button_clicked)
    # Container 3: UNSOLD button
    with st.container(border=True):
        unsold_button = st.button('**PLAYER UNSOLD**', on_click=unsold_player,use_container_width=True,disabled=not st.session_state.buttons_enabled or st.session_state.unsold_button_clicked)
    # Container 4: Text output space
    with st.container(border=True):
        players_sold_count = masterdf[masterdf['status']=='sold']['status'].count()
        players_unsold_count = masterdf[masterdf['status']=='unsold']['status'].count()
        player_unauctioned_count= masterdf[masterdf['status']=='unauction']['status'].count()
        auctioned_count=players_sold_count+players_unsold_count
        total_enrolled_count=len(list(st.session_state.players_data.keys()))
        pending_count=total_enrolled_count-auctioned_count
        st.write("Sold = ",str(players_sold_count))
        if st.session_state.exit_button_clicked:
            unsold_msg = f"Unsold = {str(players_unsold_count+player_unauctioned_count)} [includes {player_unauctioned_count} unauctioned]"
            # print(unsold_msg)
            st.write(unsold_msg)
        else:    
            st.write("Unsold = ",str(players_unsold_count+player_unauctioned_count))
        st.write(f"Auctioned so far = {auctioned_count}")
        if pending_count<=0:
            pending_count=0
        st.write(f"Pending for auction= {pending_count}")
    # Complete the process
    with st.container(border=True):
        exit_button = st.button('**EXIT**', on_click=exit_auction,help='Use this button after auction is complete.',\
                                use_container_width=True,disabled=not st.session_state.exit_button_enabled or st.session_state.exit_button_clicked)
    st.text("")
    st.text("Developed by Pradeep Godi")

# Main Page Layout with Tabs
player_tab, sold_tab,unslod_tab,wallet_tab,log_tab = st.tabs(["Player Profile", "Sold","Unsold","Wallet","Log"])
with player_tab:
    #check imgae orientation
    ref_image = Image.open(st.session_state.image_url)
    oriented_image,orientation_corrected=potrait_image_orientation(ref_image)
    if orientation_corrected:
        # display_image= oriented_image
        display_image=resize_image(oriented_image,1280,853)
    else:
        display_image=resize_image(oriented_image,1280,853)
        display_image=st.session_state.image_url
    st.image(display_image, use_container_width=True)
    player_col, sell_msg_col = st.columns([1,1])
    with player_col:
        st.header(f"{st.session_state.player_name}")
        st.header(f"{st.session_state.player_style}")
    with sell_msg_col:
        st.header(st.session_state.sell_message)
with sold_tab:
    # Table Tab: Display the sold players DataFrame
    if not st.session_state.df.empty:
        masterdf = pd.read_csv(MASTER_DF_CSV)   
        for captain_name in captain_names:
            if captain_name !='None':
                player_list=list(masterdf[(masterdf['captain']==captain_name) & (masterdf['status']=='sold')]['player'])
                player_list=player_list + ([np.nan] * (MAX_PLAYERS_PER_TEAM - len(player_list)))
                st.session_state.df[captain_name]=player_list
        col_order=list(set(masterdf['captain'].values))
        st.dataframe(st.session_state.df, use_container_width=True,hide_index=False)       
        # st.dataframe(st.session_state.df, use_container_width=True,hide_index=False,column_order=col_order)
    else:
        st.write("No data to display. Click FETCH to load data.")
with unslod_tab:
    # Table Tab: Display the unsold players DataFrame
    with st.container(border=True):
        if not st.session_state.unsolddf.empty:
            masterdf = pd.read_csv(MASTER_DF_CSV)
            masterdf['phone']=masterdf['phone'].astype('string')
            st.session_state.unsolddf =masterdf[(masterdf['status']=='unsold') | (masterdf['status']=='unauction')][['player', 'phone', 'wing']].reset_index(drop=True)
            st.dataframe(st.session_state.unsolddf, use_container_width=True,hide_index=False,column_config={"phone": st.column_config.TextColumn("phone",default="st.")})      
        else:
            st.session_state.unsolddf = masterdf[masterdf['status']=='unsold'][['player', 'phone', 'wing']].reset_index(drop=True)
            st.dataframe(st.session_state.unsolddf, use_container_width=True,hide_index=False,column_config={"phone": st.column_config.TextColumn("phone",default="st.")})      
            # st.write("No data to display. Click FETCH to load data.")
with wallet_tab:
    # Table Tab: Display the captain wallet DataFrame
    with st.container(border=True):
        if not st.session_state.walletdf.empty:
            st.session_state.walletdf.reset_index(inplace=True,drop=True)
            st.session_state.walletdf = get_min_balance_required_max_price_spent_per_player(st.session_state.walletdf)
            st.session_state.walletdf.replace(to_replace=np.nan, value=0, inplace=True)
            st.session_state.walletdf= st.session_state.walletdf[[ 'captain', 'balance', 'min balance required','max spent per player','total spent', 'player']]
            # st.session_state.walletdf.rename(columns={'player':'# players purchased'},inplace=True)
            st.dataframe(st.session_state.walletdf.sort_values(by='captain'),use_container_width=True,hide_index=True)
        else:
            st.write("No data to display. Click FETCH to load data.")
with log_tab:
    # Log Tab: Display the log file 
    with st.container(border=True):
        st.session_state.log_df = pd.read_csv(MASTER_DF_CSV)
        st.dataframe(st.session_state.log_df[['date', 'captain','player', 'status', 'price']].sort_values(by='date',ascending=False),use_container_width=True,hide_index=True)


