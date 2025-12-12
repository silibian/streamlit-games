#!/usr/bin/env python
# coding: utf-8

import requests
import streamlit as st
from bs4 import BeautifulSoup
from datetime import date, time, datetime

url = "https://store.steampowered.com/explore/new/"
response = requests.get(url)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "html.parser")
game_list = soup.find("div", class_="tab_content_items")


@st.cache_data
def scrape_game_info():
	popular_new_games = []
	for game_link in game_list.find_all("a", class_="tab_item"):
		url = game_link["href"]
		name = game_link.find("div", class_="tab_item_name").text
		small_banner = game_link.find("img", class_="tab_item_cap_img")["src"]
		price = game_link.find("div", class_="discount_final_price").text
		discount = game_link.find("div", class_="discount_pct")
		discount = discount.text if discount is not None else ""
		tags = "".join(tag.text for tag in game_link.find_all("span", class_="top_tag"))

		popular_new_games.append(
			{
				"name": name,
				"url": url,
				"small_banner": small_banner,
				"price": price,
				"discount": discount,
				"tags": tags,
			}
		)

	return popular_new_games


@st.cache_data
def scrape_game_details(url):
	game_page_response = requests.get(url)
	game_page_response.encoding = "urf-8"
	game_page_soup = BeautifulSoup(game_page_response.text, "html.parser")
	game_details = game_page_soup.find("div", class_="glance_ctn")

	large_banner = game_details.find("img", class_="game_header_image_full")["src"]
	description = game_details.find("div", class_="game_description_snippet")
	description = description.text if description is not None else ""
	release_date = game_details.find("div", class_="date").text
	release_date = datetime.strptime(release_date, "%d %b, %Y").strftime("%d/%m/%Y")
	publisher = game_details.find("div", id="developers_list").text

	return {
		"description": description,
		"large_banner": large_banner,
		"release_date": release_date,
		"publisher": publisher,
	}


st.set_page_config(layout="wide", page_title="Nouveaux Jeux Populaires Sur Steam")
st.session_state.game_data = scrape_game_info()
st.session_state.display_count = 10


def load_more():
	st.session_state.display_count += 10


@st.dialog("Détails du jeu")
def show_details_dialog(game):
	details = scrape_game_details(game["url"])
	st.title(game["name"])
	st.image(details["large_banner"], width="stretch")
	st.markdown(f"**Date de sortie:** {details['release_date']}")
	st.markdown(f"**Développeur:** {details['publisher']}")
	st.markdown(f"**Prix:** **{game['price']}**")
	st.markdown(f"**Catégories:** {game['tags']}")

	st.divider()
	st.markdown("### Description")
	st.write(details["description"])

	st.link_button("Voir sur Steam", game["url"], use_container_width=True, type="secondary")
	# if st.button("Fermer"):
	# 	st.rerun()


st.title("Nouveaux Jeux Populaires Sur Steam")

games_to_display = st.session_state.game_data[:st.session_state.display_count]
remaining_games = len(st.session_state.game_data) - st.session_state.display_count

n_cols = 5
cols = st.columns(n_cols) 

for i, game in enumerate(games_to_display):
	with cols[i % n_cols]:
		with st.container(border=True):
			st.image(game["small_banner"], width="content")
			st.subheader(game["name"])
			st.caption(f"**Catégories:** {game['tags']}")
			st.markdown(f"**Prix:** **{game['price']}**")
			if st.button("Détails...", key=f"btn_{i}"):
				show_details_dialog(game)

if remaining_games > 0:
	st.button(
		f"Afficher plus ({remaining_games} jeu(x) restant(s))", 
		on_click=load_more, 
		use_container_width=True, 
		type="primary"
	)
