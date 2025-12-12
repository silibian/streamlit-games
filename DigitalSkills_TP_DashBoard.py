#!/usr/bin/env python
# coding: utf-8

# In[37]:


import requests
import streamlit as st
from bs4 import BeautifulSoup


# In[4]:


url = "https://store.steampowered.com/explore/new/"
response = requests.get(url)
response.encoding = "utf-8"
response


# In[28]:


soup = BeautifulSoup(response.text, "html.parser")
game_list = soup.find("div", class_="tab_content_items")
#print(repr(game_list))


# In[29]:


#popular_new_games = []


# In[39]:


def scrape_game_info():
	popular_new_games = []
	for game_link in game_list.find_all("a", class_="tab_item"):
		url = game_link["href"]
		name = game_link.find("div", class_="tab_item_name").text
		small_banner = game_link.find("img", class_="tab_item_cap_img")["src"]
		price = game_link.find("div", class_="discount_final_price").text
		discount = game_link.find("div", class_="discount_pct")
		discount = discount.text if discount is not None else ""
		tags = [tag.text for tag in game_link.find_all("span", class_="top_tag")]

		game_page_response = requests.get(url)
		game_page_response.encoding = "urf-8"
		game_page_soup = BeautifulSoup(game_page_response.text, "html.parser")
		game_details = game_page_soup.find("div", class_="glance_ctn")

		large_banner = game_details.find("img", class_="game_header_image_full")["src"]
		#description = game_details.find("div", class_="game_description_snippet").text



		popular_new_games.append(
			{
				"name": name,
				"description": ...,
				"url": url,
				"small_banner": small_banner,
				"large_banner": large_banner,
				"price": price,
				"release_date": ...,
				"publisher": ...,
				"discount": discount,
				"tags": tags,
			}
		)

	return popular_new_games

game_info = scrape_game_info()


# In[42]:


st.set_page_config(layout="wide", page_title="Nouveaux Jeux Populaires Sur Steam")
st.session_state.game_data = game_info
st.session_state.display_count = 10


# In[43]:


def load_more():
	st.session_state.display_count += 10


# In[ ]:


st.title("Nouveaux Jeux Populaires Sur Steam")

# Get the games to display based on the current count
games_to_display = st.session_state.game_data[:st.session_state.display_count]
remaining_games = len(st.session_state.game_data) - st.session_state.display_count

# --- Display Games in Cards ---
# Using 3 columns for a clean card layout
cols = st.columns(3) 

for i, game in enumerate(games_to_display):
	with cols[i % 3]: # Cycle through the 3 columns
		# Create a Streamlit container to act as a 'card'
		with st.container(border=True):
			st.image(game["small_banner"], use_column_width="auto") # Replace with the actual image URL
			st.subheader(game["name"])
			st.caption(f"**Tags:** {', '.join(game['tags'])}")
			st.markdown(f"**Price:** **{game['price']}**")
			# Button to open the dialog (pop-up)
			if st.button("View Details", key=f"btn_{i}"):
				st.session_state.selected_game_url = game["url"]
			    # Rerun the app to trigger the dialog below
# --- "Load More" Button ---
if remaining_games > 0:
	st.button(
		f"Load More ({remaining_games} remaining)", 
		on_click=load_more, 
		use_container_width=True, 
		type="primary"
	)

# --- 4. Dialog/Pop-up Logic ---
if 'selected_game_url' in st.session_state and st.session_state.selected_game_url:
	with st.dialog("Game Details"):
		# Scrape and display the details for the selected game
		#details = scrape_game_details(st.session_state.selected_game_url)

		# Find the game's summary info again (for name, price, etc.)
		selected_game = next(
			(g for g in st.session_state.game_data if g["url"] == st.session_state.selected_game_url), 
			None
		)
		details = selected_game
		if selected_game:
			st.title(selected_game["name"])
			st.image(details["large_banner"], use_column_width="auto") # Replace with banner image
			st.markdown(f"**Release Date:** {details['release_date']}")
			st.markdown(f"**Publisher/Developer:** {details['publisher']}")
			st.markdown(f"**Price:** **{selected_game['price']}**")
			st.markdown(f"**Tags:** {', '.join(selected_game['tags'])}")

			st.divider()
			st.markdown("### Description")
			st.write(details["description"])

			# Button that links to the original Steam page
			st.link_button("View on Steam", selected_game["steam_url"], use_container_width=True, type="secondary")
			# Clean up the session state when the user is done with the dialog
			if st.button("Close"):
				st.session_state.selected_game_url = None
				st.rerun() 
		else:
			st.error("Game details not found.")

