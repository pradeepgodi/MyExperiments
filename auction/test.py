import streamlit as st
import pandas as pd
import json
import os
import random
import datetime
import numpy as np
from PIL import ImageDraw,Image,ExifTags,ImageOps

# Styling for Sidebar buttons
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #DFFFFF;
            color: blue;
            # font-weight: bold;
            # .dataframe {text-align: left !important}

        # .stButton button {
        # background-color: white;
        # border: 1px solid black;} 
        
        # .st-ag {
        # outline: 1px solid blue;
        # # border: 1px solid blue;
        # }  
            
    # .stHeading {
    # padding: 0 30px; 
    # white-space: nowrap; 
}

    }
</style>""", unsafe_allow_html=True)

def makedir(name):
    try:
        os.makedirs(name)
        print("created new folder =",name)
    except OSError:
        pass    

makedir('sold_players')
makedir('unsold_players')
makedir('teams')

# create master dataframe/csv to capture all activities
if not os.path.isfile('masterdf.csv'):
    master_columns=['date','captain','player','status','price','phone','wing']
    masterdf =pd.DataFrame(columns=master_columns)
    masterdf.to_csv('masterdf.csv',index=False)

# Get the list of Captains, purse value, number of players 
print(os.name,os.curdir,os.getcwd())
captaindf = pd.read_csv('\\MyExperiments\\auction\\captains.csv')
order_names=list(captaindf['name'])
order_names.sort()
captainNames = ['None']+order_names
numberOfPlayers=captaindf['players'][0]
total_purse_value=int(captaindf['purse'][0])


# Get the list of all players and dump them into a json file
st.session_state.players_data={}
for player in os.listdir(path=".\\enrolled_players"):
    player_list=player.split('_')
    player_list.append(player)
    # st.session_state.players_data[player_list[0].upper()]=player_list[1:]  
    st.session_state.players_data[player_list[0]]=player_list[1:]  
# Convert and write JSON object to file
with open("players_data.json", "w") as outfile: 
    json.dump(st.session_state.players_data, outfile)

# Function to get the new player randomly
def get_new_player():
    with open("players_data.json") as json_file:
        players_data = json.load(json_file)
    enrolled_players= list(players_data.keys())

    masterdf = pd.read_csv('masterdf.csv')
    auctioned_players_list = masterdf['player'].unique()
    try:
        player_for_auction=random.choice(list(set(enrolled_players) - set(auctioned_players_list)))
        print("Player randomly selected for auction = ",player_for_auction,players_data[player_for_auction])
        return player_for_auction,players_data[player_for_auction]
    except:
        st.warning("All Players are Auctioned.Click on EXIT button.",icon="⚠️")
        st.session_state.exit_button_enabled = True
        st.session_state.price_input = st.session_state.widget
        st.session_state.widget = ""
        st.session_state.selection_reset = 'None'
        st.session_state.fetch_button_enabled=False  
        return False, False

def get_count_of_players_auctioned():
    auction_pending_players=os.listdir('players')
    sold_players=os.listdir('sold_players')
    unsold_players=os.listdir('unsold_players')
    return auction_pending_players,sold_players,unsold_players

# Function Definitions for Button Actions
def fetch_data():
    print("Fetching new player for aution.")
    player_for_auction,player_metadata=get_new_player()
    if player_for_auction and player_metadata :
        st.session_state.player_name = player_for_auction
        st.session_state.player_wing = player_metadata[0]
        st.session_state.player_ph = player_metadata[1]
        st.session_state.player_style = player_metadata[2].split(".")[0]
        
        st.session_state.image_url = ".\\enrolled_players\\"+ player_metadata[-1]
        # print("Player image =",st.session_state.image_url)
        st.session_state.df = pd.DataFrame(columns=captainNames[1:],index=range(numberOfPlayers))

        # Reset the previous BID price and captain selection values before new fetching of the players
        st.session_state.price_input = st.session_state.widget
        st.session_state.widget = ""
        st.session_state.selection_reset = 'None'
        st.session_state.sell_message =" "
        # st.session_state.emoji =" "

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
        st.session_state.image_url= ".\\default_image.jpg" 
        st.session_state.sell_message =" "
        # st.session_state.emoji =" "
        st.session_state.player_name ="Player Name"
        st.session_state.player_style = "Playing Style"     




def sell_player():
    # disable sold and unsold button ater clicking once
    st.session_state.sell_button_clicked = True
    st.session_state.unsold_button_clicked = True

    if not (st.session_state.captain_choice =='None' or st.session_state.price_input ==''):
        # # create player records for book keeping
        d=str(datetime.datetime.now())
        sell_date=d.split(" ")[0] +'_' +d.split(" ")[1].split('.')[0]
        player_sell_record = [ sell_date,st.session_state.captain_choice,
                                st.session_state.player_name,'sold',st.session_state.price_input,
                                st.session_state.player_ph,st.session_state.player_wing ]
        masterdf = pd.read_csv('masterdf.csv') 
        # # Check wallet if player can be sold to a the captain
        captain_wallet_price_balance=total_purse_value-masterdf[masterdf['captain']==st.session_state.captain_choice]['price'].sum()
        captain_wallet_player_count =masterdf[masterdf['captain']==st.session_state.captain_choice]['player'].count()
        st.session_state.sell_condition =  (int(st.session_state.price_input) <= int(captain_wallet_price_balance) and (captain_wallet_player_count<numberOfPlayers) )
        # print('sell_condition =',st.session_state.sell_condition,captain_wallet_price_balance,captain_wallet_player_count)
        if st.session_state.sell_condition:
            # print('allowed to bid and purchase')
            print(f"Captain wallet={st.session_state.captain_choice},bal={captain_wallet_price_balance},spent={total_purse_value-captain_wallet_price_balance},player= {captain_wallet_player_count}")

            masterdf.loc[len(masterdf.index)] = list(player_sell_record)
            masterdf.to_csv('masterdf.csv',index=False)
            st.session_state.players_sold_count = str(masterdf[masterdf['status']=='sold']['status'].count())
            st.session_state.sell_message = f"Sold to {st.session_state.captain_choice} for {st.session_state.price_input}"
            total_sold_player_count=masterdf[masterdf['status']=='sold'].shape[0]
            # print('total player sold=',total_sold_player_count)
            if total_sold_player_count == numberOfPlayers*len(order_names):
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
            st.session_state.walletdf.loc[row_id,'spent']=price_value
            st.session_state.walletdf.loc[row_id,'player']=player_count_value
            st.session_state.walletdf.loc[row_id,'balance']=total_purse_value-price_value

            with open("players_data.json") as json_file:
                players_data = json.load(json_file)
            if  len(players_data.keys())==  len(masterdf['player'].unique()):
                st.session_state.exit_button_enabled=True
            print("Player sell record = ",player_sell_record)
        else:
            print("Captian has exceeded the wallet budget")
            print(f"Captain={st.session_state.captain_choice},bal={captain_wallet_price_balance},player= {captain_wallet_player_count},purse & player = {total_purse_value} & {numberOfPlayers}")
            msg = f"Wallet balance price ={captain_wallet_price_balance} and purchased players ={captain_wallet_player_count}"
            st.session_state.sell_message=f"Wallet exceeded.Don't be greedy {st.session_state.captain_choice}."
            st.session_state.sell_button_clicked = False
            st.session_state.unsold_button_clicked = False

            st.session_state.wallet_exceeded_captains.append(st.session_state.captain_choice)
    else:
        print("bid price or empty captain name")
        st.session_state.sell_message="Enter correct BID price and select CAPTAIN name."
        st.session_state.buttons_enabled =True
        st.session_state.sell_button_clicked =False   


def unsold_player():
    # disable sold and unsold button ater clicking once
    st.session_state.sell_button_clicked = True
    st.session_state.unsold_button_clicked = True   
    # create player records for book keeping
    d=str(datetime.datetime.now())
    sell_date=d.split(" ")[0] +'_' +d.split(" ")[1].split('.')[0]
    player_unsell_record = [ sell_date,'None',
                            st.session_state.player_name,'unsold','None',
                            str(st.session_state.player_ph),st.session_state.player_wing ]
    
    st.session_state.sell_message = f"UNSOLD !!!"
    # st.session_state.emoji = ":disappointed:"
    masterdf = pd.read_csv('masterdf.csv') 
    masterdf.loc[len(masterdf.index)] = list(player_unsell_record)
    masterdf.to_csv('masterdf.csv',index=False)
    st.session_state.players_unsold_count = str(masterdf[masterdf['status']=='unsold']['status'].count())

    with open("players_data.json") as json_file:
        players_data = json.load(json_file)
    if  len(players_data.keys())==  len(masterdf['player'].unique()):
        st.session_state.exit_button_enabled=True
    print("Player unsold record=",player_unsell_record)

def exit_auction():
    # # Move sold and unsold players to separate folders
    print("clicked on exit button")
    st.session_state.image_url= ".\\default_image.jpg" 
    st.session_state.player_name =""
    st.session_state.player_style = "" 
    st.session_state.sell_message =""
    # st.session_state.emoji =""      
    masterdf = pd.read_csv('masterdf.csv') 
    with open("players_data.json") as json_file:
        players_data = json.load(json_file)
        # print("player_data",players_data)

    sold_players=list(masterdf[masterdf['status']=='sold']['player'])
    unsold_players=list(masterdf[masterdf['status']=='unsold']['player'])
    unauctioned_players=list(set(players_data.keys()).difference(set(sold_players).union(set(unsold_players))))

    # add unauction player to the master df
    d=str(datetime.datetime.now())
    sell_date=d.split(" ")[0] +'_' +d.split(" ")[1].split('.')[0]
    for player in unauctioned_players:
        unauction_record= [sell_date,'None',player,'unauction',np.nan,str(players_data[player][1]),players_data[player][0]]
        # print(unauction_record)
        masterdf.loc[masterdf.shape[0]]=unauction_record
    masterdf.to_csv('masterdf.csv',index=False)
    print("Sold players" ,len(sold_players),sold_players) 
    print("Unsold players",len(unsold_players),unsold_players) 
    print("Unauctioned players",len(unauctioned_players),unauctioned_players) 
    if len(players_data.keys())>0:       
        for sold in sold_players:
            # print(players_data[sold][-1])
            image_to_move=players_data[sold][-1]
            source = ".\\enrolled_players\\"+image_to_move
            destination=".\\sold_players\\"+image_to_move   
            os.rename(source, destination)                         
        for unsold in unsold_players:
            # print(players_data[unsold][-1])
            image_to_move=players_data[unsold][-1]
            source = ".\\enrolled_players\\"+image_to_move
            destination=".\\unsold_players\\"+image_to_move   
            os.rename(source, destination)   
        for unauction in unauctioned_players:
            # print(players_data[unauction][-1])
            image_to_move=players_data[unauction][-1]
            source = ".\\enrolled_players\\"+image_to_move
            destination=".\\unsold_players\\"+image_to_move   
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
        if captain =='None':
            file_name = "unsold_players.csv"
        else:
            file_name = f"{captain}'s_team.csv"
        print("Creating teams =",file_name)
        masterdf[masterdf['captain']==captain].reset_index(drop=True).to_csv(".\\teams\\"+file_name)

    # creating the final wallet table in the end
    st.session_state.walletdf.reset_index(drop=True).to_csv(".\\teams\\"+"wallet.csv")

    # creating final sold table in the end
    masterdf = pd.read_csv('masterdf.csv')
    solddf=masterdf[masterdf['status']=='sold'][['captain','player']]
    data={}
    for cap in solddf['captain'].unique():
        data[cap]=solddf[solddf['captain']==cap]['player'].to_list()
    pd.DataFrame(data=data).reset_index(drop=True).to_csv(".\\teams\\"+"sold.csv")


def crop_image(image):
    print("Cropping the image")  
    image = Image.open(image)
    new_image = image.resize((1280, 853))
    # new_image.save('myimage_500.jpg')
    return new_image


def resize_image(image, width, height):
    # print("Resizing the image to ", width, height)
    image_thumbnail = image.copy()
    image_thumbnail.thumbnail((width, height))
    # print(f"The image re-sized to = {image_thumbnail.size}.")

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


# Initialize session state for dynamic elements
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=captainNames[1:],index=range(numberOfPlayers))
if 'unsolddf' not in st.session_state:
    masterdf = pd.read_csv('masterdf.csv')  
    st.session_state.unsolddf =masterdf[(masterdf['status']=='unsold') | (masterdf['status']=='unauction')][['date', 'player', 'phone', 'wing']].reset_index(drop=True)
if 'walletdf' not in st.session_state:
    if masterdf.empty:
        walletdf = pd.DataFrame(data={'captain':captainNames[1:]})
        walletdf[['balance']]=[total_purse_value]
        walletdf[['spent']]=[0]
        walletdf[['player']]=[0]
        st.session_state.walletdf = walletdf
    else:
        df1=masterdf[['captain','price']].groupby(['captain']).sum()['price'].to_frame().reset_index().sort_values(by='captain')
        df2=masterdf[['captain','player']].groupby(['captain']).count()['player'].to_frame().reset_index().sort_values(by='captain')
        walletdf=df1.merge(df2,how='inner', on='captain')
        walletdf['balance'] = total_purse_value - walletdf['price']
        walletdf.rename(columns={'price':'spent'},inplace=True)
        walletdf=walletdf[['captain', 'balance','spent', 'player']]
        name_diff=list(set(captainNames[1:])-set(walletdf['captain'].values))
        df3 = pd.DataFrame(data={'captain':name_diff})
        df3[['balance']]=[total_purse_value]
        df3[['spent']]=[0]
        df3[['player']]=[0]
        st.session_state.walletdf=pd.concat([walletdf,df3])
if 'players_sold_count' not in st.session_state:
    masterdf = pd.read_csv('masterdf.csv')  
    st.session_state.players_sold_count = str(masterdf[masterdf['status']=='sold']['status'].count())
if 'players_unsold_count' not in st.session_state:
    st.session_state.players_unsold_count = str(masterdf[masterdf['status']=='unsold']['status'].count())
if 'players_data' not in st.session_state:
    st.session_state.players_data={}    
if 'auction_pending_count' not in st.session_state:
    st.session_state.auction_pending_count = str((len(list(st.session_state.players_data.keys())) - (int(st.session_state.players_sold_count)+int(st.session_state.players_unsold_count))))   
if 'image_url' not in st.session_state:
    # Set default image (dummy image) when the app first loads
    st.session_state.image_url = ".\\default_image.jpg" 
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
            masterdf = pd.read_csv('masterdf.csv')      
            df=masterdf[['captain','player']].groupby(['captain']).count().reset_index()
            captain_drop_down_list=list(df[df['player']==numberOfPlayers]['captain'].values)
            captain_drop_down_list= list(set(captainNames)-(set(captain_drop_down_list)))
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


# Main Page Layout with Tabs
player_tab, sold_tab,unslod_tab,wallet_tab = st.tabs(["Player Profile", "Sold","Unsold","Wallet"])
with player_tab:
    #check imgae orientation
    ref_image = Image.open(st.session_state.image_url)
    oriented_image,orientation_corrected=potrait_image_orientation(ref_image)
    if orientation_corrected:
        display_image= oriented_image
        display_image=resize_image(oriented_image,1280,853)
    else:
        display_image=resize_image(oriented_image,1280,853)
        display_image=st.session_state.image_url
    # print("Corrected Image size after  = ",display_image.size)
    # display_image=crop_image(oriented_image)    
    st.image(display_image, use_column_width=True)
    player_col, sell_msg_col = st.columns([1,1])
    with player_col:
        st.header(f"{st.session_state.player_name}")
        st.header(f"{st.session_state.player_style}")
    with sell_msg_col:
        st.header(st.session_state.sell_message)
with sold_tab:
    # Table Tab: Display the sold players DataFrame
    if not st.session_state.df.empty:
        masterdf = pd.read_csv('masterdf.csv')   
        for captain_name in captainNames:
            if captain_name !='None':
                player_list=list(masterdf[(masterdf['captain']==captain_name) & (masterdf['status']=='sold')]['player'])
                player_list=player_list + ([np.nan] * (numberOfPlayers - len(player_list)))
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
            masterdf = pd.read_csv('masterdf.csv')
            masterdf['phone']=masterdf['phone'].astype('string')
            st.session_state.unsolddf =masterdf[(masterdf['status']=='unsold') | (masterdf['status']=='unauction')][['date', 'player', 'phone', 'wing']].reset_index(drop=True)
            st.dataframe(st.session_state.unsolddf, use_container_width=True,hide_index=False,column_config={"phone": st.column_config.TextColumn("phone",default="st.")})      
        else:
            st.session_state.unsolddf = masterdf[masterdf['status']=='unsold'][['date', 'player', 'phone', 'wing']].reset_index(drop=True)
            st.dataframe(st.session_state.unsolddf, use_container_width=True,hide_index=False,column_config={"phone": st.column_config.TextColumn("phone",default="st.")})      
            # st.write("No data to display. Click FETCH to load data.")
with wallet_tab:
    # Table Tab: Display the captain wallet DataFrame
    with st.container(border=True):
        if not st.session_state.walletdf.empty:
            st.dataframe(st.session_state.walletdf.sort_values(by='captain'),use_container_width=True,hide_index=True)
        else:
            st.write("No data to display. Click FETCH to load data.")


