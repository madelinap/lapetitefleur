import streamlit as st
# from streamlit_searchbox import st_searchbox
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
from  PIL import Image
import numpy as np
import pandas as pd
import leafmap.foliumap as leafmap
import folium
import folium.plugins as plugins
from folium.plugins import MarkerCluster
import branca
import platform
import urllib.parse
from streamlit.components.v1 import html
# import streamlit.components.v1 as components
# import datetime

import platform
# from streamlit_modal import Modal
import streamlit.components.v1 as components
# from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
import openai
import pinecone

syst = '.' if platform.system() == 'Windows' else '/app'
img = Image.open(f"{syst}/static/lapetitefleur.png")
pc = st.get_option('theme.primaryColor')
tc = st.get_option('theme.textColor')

all_option = "Toutes les catégories..."
chat_warn = "Veuillez noter que les informations fournies sont basées sur les commentaires des utilisateurs et peuvent être sujettes au changement."
slider_traveltime_min = 0
slider_traveltime_max = 90
search_empty_text = "Search..."
legend_max = 20
map_height = 325
limit = 50000

PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_API_ENV = st.secrets["PINECONE_API_ENV"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# openai.api_key = st.secrets["OPENAI_API_KEY"]
embed_model = "text-embedding-ada-002"

if 'step_selection' not in st.session_state:
	st.session_state.step_selection = all_option

if 'prev_selection' not in st.session_state:
	st.session_state.prev_selection = ''
	
if 'map_full' not in st.session_state:
	st.session_state.map_full = []

if 'map_filt' not in st.session_state:
	st.session_state.map_filt = []

if 'show_map' not in st.session_state:
	st.session_state.show_map = False
	
if 'search_k' not in st.session_state:
	st.session_state.search_k = search_empty_text

if 'radio_ischanged' not in st.session_state:
	st.session_state.radio_ischanged = 0
	
if "grid_key" not in st.session_state:
    st.session_state.grid_key = 0

if "show_onmap" not in st.session_state:
	st.session_state.show_onmap = []

if "prev_show_onmap" not in st.session_state:
	st.session_state.prev_show_onmap = []	

if "indices" not in st.session_state:
	st.session_state.indices = None

if 'zoom_level' not in st.session_state:
	st.session_state.zoom_level = None

if 'grid_selrows' not in st.session_state:
	st.session_state.grid_selrows = None	

if 'icon_dict' not in st.session_state:
	st.session_state.icon_dict = {}

if 'pre_selected_rows' not in st.session_state:
	st.session_state.pre_selected_rows = []

if 'radio_id' not in st.session_state:
	st.session_state.radio_id = 1

if 'indexview' not in st.session_state:
	st.session_state.indexview = 0

if 'ai' not in st.session_state:
	st.session_state.ai = 0

if 'x' not in st.session_state:
	st.session_state.x = 0	

try:
	st.session_state.open = int(st.experimental_get_query_params()['open'][0])
except:
	st.session_state.open = 0

if "messages" not in st.session_state:
	st.session_state.messages = []

if "index" not in st.session_state:   
	pinecone.init(      
		api_key=PINECONE_API_KEY,
		environment=PINECONE_API_ENV      
	) 
	st.session_state.index = pinecone.Index('placesreviews')

if 'lang' not in st.session_state:
	st.session_state.lang = 'fr'

try:
	st.session_state.lang = st.experimental_get_query_params()['lang'][0]
except:
	st.session_state.lang = 'fr'

col_activity       = 'activity_fr'
col_category       = 'category_fr'
col_super_category = 'super_category_fr'
col_tags           = 'tags_fr'
val_others         = 'Autres'

def local_css(file_name):
    f = open(file_name)
    styling = f.read()
    # print(styling)
    st.markdown(f"<style>{styling}</style>", unsafe_allow_html=True)    
    return True
   
# styling
st.set_page_config(
	layout="wide",
	page_title='lapetitefleur',
	page_icon=img,
	)

local_css("style.css")

def main():
	page_search()
    
def page_search():
	# st.json(st.session_state)
	st.session_state.x = st.session_state.x + 1
	st.session_state.messages = []
	st.session_state.radio_ischanged = 1 if st.session_state.prev_selection != st.session_state.step_selection else 0
	st.session_state.prev_selection = st.session_state.step_selection
	if st.session_state.radio_ischanged == 1:
		if 'keyword_searchbox' in st.session_state:
			st.session_state.keyword_searchbox['search'] = ""
			st.session_state.keyword_searchbox['options'] = []

	if 'selectbox_city' in st.session_state:
		lbl_city = st.session_state.selectbox_city + "  -  " + str(st.session_state.slider_dist ) + "min"
		if 'selectbox_city_prev' in st.session_state:
			if st.session_state.selectbox_city_prev != st.session_state.selectbox_city:
				st.session_state.messages = []
		if 'slider_dist_prev' in st.session_state:
			if st.session_state.slider_dist_prev != st.session_state.slider_dist:
				st.session_state.messages = []				
		st.session_state.selectbox_city_prev = st.session_state.selectbox_city
		st.session_state.slider_dist_prev = st.session_state.slider_dist
	else:
		lbl_city = f"Montréal - {str(slider_traveltime_max)}min"

	with st.expander(lbl_city, expanded=False):
		top()
	
	st.radio(
			label = "tabviewmain",
			options = ("Recherche", "Assistant IA"),
			index = st.session_state.open,
			horizontal = True,
			label_visibility = "collapsed",
			key = "tabviewmain"
	)

	if st.session_state.tabviewmain == "Recherche":
		# with st.expander("Selectionez votre activite", expanded=True):
		st.markdown(f'<p style="color:#D87D92;font-weight:700;">Selectionez votre activite:</p>', unsafe_allow_html=True)
		category()
		map, df_main = buildmap()
		build_multiselect()
		# st.write("_" * 34)

		tabview = st.radio(
			label = "tabview",
			options = ["Carte","Liste"],
			index = st.session_state["indexview"],
			horizontal = True,
			label_visibility = "collapsed",
			key = st.session_state.radio_id
		)
		if tabview == "Carte":
			st.session_state["indexview"] = 0
			if not map is None:
				map.to_streamlit(width=None, height=map_height, scrolling=False)
			else:
				st.write("Selectionez un endroit")
		else:
			st.session_state["indexview"] = 1
			draw_aggrid_df(df_main)	
	else:
		# st.session_state["indexview"] = 2
		assistant()

	return True


def assistant():
	prompt = None
	questions = [
		"Où je peux faire de la randonnée facile avec mes enfants?",
		"Les places où je peux cueillir des framboises.",
		"Où je peux trouver des sentiers accessibles en fauteuil roulant?",
		"Où je peux organiser un mariage en nature?",
		"Où je peux trouver des produits frais de la ferme?",
		# "Les places où je peux admirer les couleurs de l'automne.",
		"Les endroits ou je peux faire du vélo montagne."
	]
	
	def retrieve(query, n, index):
		prompt = None
		try:
			_, distances = prep_data()
			res = openai.Embedding.create(
				input=[query],
				engine=embed_model
			)
			
			query = query + "Start with a short introduction. Provide extensive details, the website and the directions for each of the places."
			# retrieve from Pinecone
			xq = res['data'][0]['embedding']

			# get relevant contexts
			rez = index.query(xq, top_k=n, include_metadata=True)
			# print('matches=', rez['matches'])
			list_of_match_places = list([int((x['metadata']['index'])) for x in rez['matches']])
			# print("len=", len(list_of_match_places))

			places_selected = list(distances[
				(distances['time_min'] <= st.session_state.slider_dist) & 
				(distances['city'] == st.session_state.selectbox_city) & 
				(distances['place_idx'].isin(list_of_match_places))]['place_idx'])

			rez_filtred = pd.DataFrame(
				[x['metadata'] for x in rez['matches'] if int(x['metadata']['index']) in places_selected]
			).drop_duplicates(subset=['index'])
			
			# print("rez_filtred=", rez_filtred.shape)
			rand = 20 if rez_filtred.shape[0] >= 20 else rez_filtred.shape[0]
			contexts = 	[
				"The name of this place is: "   + 
				x['title']                      + 
				" and the website is: "         + 
				x["website"]                    + 
				", and the direction is:"       +
				"<a href = 'https://www.google.com/maps/dir/?api=1&destination=" +
				str(x["latitude"]) + "," + str(x["longitude"])                   +
				"' target='_blank'>carte</a>"   +
				x['text'] 
					for x in rez_filtred.sample(rand).to_dict('records')
			]

			if len(contexts) > 0:
				# Build prompt
				prompt_start = (
					"Answer the question in French based only on the context provided below. Answer should be embedded in html tags.\n\n"
					"Context:\n"
				)
				prompt_end = (
					f"\n\nAlways answer in French.\n\nQuestion: {query}\nAnswer:"
				)
				# append contexts until hitting limit
				for i in range(1, len(contexts)):
					if len("\n\n---\n\n".join(contexts[:i])) >= limit:
						prompt = (
							prompt_start +
							"\n\n---\n\n".join(contexts[:i-1]) +
							prompt_end
						)
						break
					elif i == len(contexts)-1:
						prompt = (
							prompt_start +
							"\n\n---\n\n".join(contexts) +
							prompt_end
						)
			else:
				prompt = None
		except:
			prompt = None
		return prompt
	
	st.markdown(f'<p style="color:#D87D92;font-weight:700;">Posez une question:</p>', unsafe_allow_html=True)
	st.selectbox(
		label = "Questions",
		help="Question modèle",
		options = ['Selectionez une  question modèle...'] + questions,
		index = 0, #st.session_state.ai,
		key = "selectbox_question",
		label_visibility = "collapsed"
	)

	prompt_chat = st.chat_input(placeholder="Posez votre propre question...", key="chat_input")
	# st.write("_" * 34)
	prompt = (prompt_chat if not prompt_chat is None else st.session_state.selectbox_question if st.session_state.selectbox_question in questions else None)

	# for message in st.session_state.messages:
	# 	html(div_scroll(message["content"]))
	# 	with st.chat_message(message["role"]):
	# 		st.markdown(message["content"])

	if not (prompt is None):
		# st.session_state.ai = 0

		with st.chat_message("user", avatar = None):
			st.markdown(prompt, unsafe_allow_html=True)

		with st.chat_message("assistant"):
			message_placeholder = st.empty()
			# st.markdown(f"<div class='mybox'>{message_placeholder}</div>", unsafe_allow_html=True)

			# def html(body):
			# 	st.markdown(body, unsafe_allow_html=True)

			# def div_scroll(txt):
			# 	return f"<div class='mybox'>{txt}</div>"
	
			# inner_html = div_scroll(message_placeholder)
			# # html(inner_html)

			full_response = ""
			messages=[
				{"role": m["role"], "content": m["content"]}
				for m in st.session_state.messages
			]

			st.session_state.messages.append({"role": "user", "content": prompt})

			# with st.spinner("Running..."):
			query_with_contexts = retrieve(query=prompt, n=100, index=st.session_state.index)
			messages.append({"role": "user", "content": query_with_contexts})
			# print("query_with_contexts=", query_with_contexts)

			if not (query_with_contexts is None):
				list_of_places = ""
				for response in openai.ChatCompletion.create(
					# model="gpt-3.5-turbo-16k",
					# model="gpt-3.5-turbo",
					model="gpt-4",
					messages=messages,
					max_tokens=2048,
					n=1,
					temperature=0.5,
					stream=True,
				):
					resp = response.choices[0].delta.get("content", "")
					# print("stream=", resp)
					list_of_places += resp		
					message_placeholder.markdown(list_of_places + "▌", unsafe_allow_html=True)
				message_placeholder.markdown(list_of_places + f'<p class="small-font">{chat_warn}</p>', unsafe_allow_html=True)
			else:
				list_of_places = "Pas des places trouvees, changez vos criteres de recherche."
				message_placeholder.markdown(list_of_places, unsafe_allow_html=True)
			
			# full_response = list_of_places + f'<p class="small-font">{chat_warn}</p>'
			# st.markdown(full_response, unsafe_allow_html=True)	
			# inner_html = div_scroll(full_response)
			# print("inner_html=", inner_html)
			# html(inner_html)

			# print("full_response=\n", full_response)
			# st.session_state.messages.append({"role": "user", "content": query_with_contexts})
			st.session_state.messages.append({"role": "assistant", "content": full_response})
			# print("history=", st.session_state.messages)


def top():
	col_city, col_dist = st.columns([0.5, 0.5])
	with col_dist:
		st.slider(
			"Distance", 
			min_value = 0, 
			max_value = 300,
			step = 10,
			value = slider_traveltime_max,
			format = "%dmin",
			key = "slider_dist",
			label_visibility = "collapsed"
		)

	with col_city:
		cities = prep_city()
		st.selectbox(
			label = "City",
			options = sorted(set(cities['city'])),
			index = 4,
			help = "Select your prefered activities...",
			key = "selectbox_city",
			label_visibility = "collapsed",
		)
	return True

def category():
	_tmp, _ = prep_data()
	radio_options = [all_option] + sorted(_tmp[col_super_category].unique())

	st.selectbox(
		label ="options:",
		key = 'step_selection',
		label_visibility = "collapsed",
		options = radio_options,
		)
	
	# print(len(_tmp['index'].unique()))
	return True

def strfdelta(td):
	td_sec = td.seconds
	hour_count, rem = divmod(td_sec, 3600)
	minute_count, second_count = divmod(rem, 60)
	msg = "{} hours {} min".format(hour_count, minute_count) if hour_count >= 1 else "{} min".format(minute_count)	
	return msg


st.cache_resource()
def draw_aggrid_df(df) -> AgGrid:
	if df.shape[0] > 0:

		# pre_selected_rows = st.session_state.pre_selected_rows
		# print("st.session_state.pre_selected_rows", st.session_state.pre_selected_rows)

		gb = GridOptionsBuilder.from_dataframe(
			df, 
			editable=True,
			)
		# gb.configure_selection(
		# 	selection_mode = "single",
		# 	pre_selected_rows = st.session_state.pre_selected_rows,
		# 	use_checkbox = True,
		# 	)
		gb.configure_column("getdirections",
			headerName="Carte...",
			cellRenderer=JsCode('''
				function(params) {return `${params.value}`}
			'''),
			maxWidth=80, 
			)	
		gb.configure_column("url",
			headerName="Les plus populaires ^",
			cellRenderer=JsCode('''
				function(params) {return `${params.value}`}
			'''),						
			# minWidth=200, 
			# maxWidth=300, 
			autoHeight=False,
			# wrapText=True,
			sortable=False,
			resizable=True,
			)	
		gb.configure_column("index",
				headerName="Index",
				minWidth=0, 
				maxWidth=0, 
				hide=True,
			)
		custom_css = {
			# ".ag-cell-value": {"padding": "1px !important", "background-color": "lightgrey"},
			# ".ag-row a": {"font-size": "15px","background-color": "lightgrey"},
			# ".ag-row i": {"font-size": "12px","background-color": "lightgrey"},
		}
		gb.configure_grid_options(
			rowHeight=60
			)
		ag_grid = AgGrid(
				data=df,
				gridOptions=gb.build(),
				height=f"{map_height}px",
				data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
				update_mode=GridUpdateMode.MODEL_CHANGED,
				allow_unsafe_jscode=True,
				enable_enterprise_modules=False,
				use_checkbox=True,
				# custom_css=custom_css,
				sizeColumnsToFit=True,
				fit_columns_on_grid_load=True,
				reload_data=False,
				# key="grid",
		)
		df = ag_grid["data"]

		if len(ag_grid["selected_rows"]) > 0:
			# save the row indexes of the selected rows in the session state
			pre_selected_rows = []
			for selected_row in ag_grid["selected_rows"]:
				# print('selected_row=', selected_row['rowIndex'])
				pre_selected_rows.append(selected_row['rowIndex'])
			st.session_state.pre_selected_rows = pre_selected_rows

			idx = [r['index'] for r in ag_grid["selected_rows"]]
			st.session_state.prev_show_onmap = st.session_state.show_onmap
			st.session_state.show_onmap = idx

			# if len(st.session_state.pre_selected_rows) > 0:
			# print("st.session_state.show_onmap", st.session_state.show_onmap, st.session_state.prev_show_onmap)
			# print('cond1:', (len(st.session_state.show_onmap) > 0) )
			# print('cond2', (not np.array_equal(st.session_state.prev_show_onmap, st.session_state.show_onmap)))

			if (len(st.session_state.show_onmap) > 0) and (not np.array_equal(st.session_state.prev_show_onmap, st.session_state.show_onmap)):
				st.session_state["indexview"] = 0
				st.session_state.radio_id += 1
				st.experimental_rerun()

	else:
		ag_grid = None
	return ag_grid

st.cache_resource()
def buildmap():
	if st.session_state.radio_ischanged == 1 or st.session_state.search_k == search_empty_text:
		activity = st.session_state.step_selection		
		st.session_state.first_option = activity + "..."
		df_activity = filt_data(activity)
		# st.session_state.pre_selected_rows = []
		# print(df_activity.columns)

		# map center logic
		if df_activity.shape[0] > 0:
			if not np.array_equal(st.session_state.indices, df_activity["index"].array):
				st.session_state.indices = df_activity["index"].array
				st.session_state.show_onmap = []
				st.session_state.pre_selected_rows = []
				st.session_state.radio_id += 1

			_tmp = df_activity.sort_values(by=['num_reviews','name'], ascending=False).reset_index()
			_tmp["rank"] = _tmp.index + 1
			# _tmp["timedelta"] = _tmp["time_min"].apply(lambda x: strfdelta(timedelta(minutes=x)))
			_tmp["getdirections"] = _tmp.apply(
				lambda x: "<a href = '"  +
				      		"https://www.google.com/maps/dir/?api=1&destination=" + 
							str(x["latitude"]) + "," + str(x["longitude"]) + 
							"' target='_blank'>" + 
							"<img src='./static/img/diamond-turn-right-solid.svg' width=16 height=16 style='opacity:0.5;'>" + "</a>"
							, axis=1)
			_tmp["url"] = _tmp.apply(
				lambda x:  	"<a href='" + str(x["contact"]) + "' target='_blank'>" + 
							str(x["name"]) + "</a>" +
							"<br><i>" + str(x[col_tags]) + "</i>"
							, axis = 1)
						
			_tmp = _tmp.drop_duplicates(subset=['name', 'latitude', 'longitude'], keep='first')

			map = generate_map(_tmp)
			res = _tmp[["getdirections","url", "index"]]

		else:
			map = None
			res = pd.DataFrame()
	else:
		map = None	
		res = pd.DataFrame()

	return map, res


def build_multiselect():
	full_list = st.session_state.map_full

	if 'map_filt_single' in st.session_state:
		st.session_state.last_map_filt_single = st.session_state.map_filt_single

	st.multiselect(
			label = "map_filt_single",
			options = full_list if len(full_list) > 1 else full_list,
			default = None if st.session_state.step_selection == all_option else (full_list if len(full_list) > 1 else full_list),
			help = "Select your prefered activities...",
			key = 'map_filt_single', # this will populate session key map_filt
			label_visibility = "collapsed",
			max_selections = 6,
	)

	# need to force reload, otherwise the multiselect session is not updating
	if 'map_filt_single' in st.session_state and 'last_map_filt_single' in st.session_state:
		if st.session_state.last_map_filt_single != st.session_state.map_filt_single:
			# st.session_state.show_onmap, st.session_state.pre_selected_rows = [], []
			st.experimental_rerun()
	
	return True


def generate_map(df):
	_cities = prep_city()
	st.session_state.map_center = list(
			_cities[_cities['city'] == st.session_state.selectbox_city][['latitude', 'longitude']].iloc[0].values)
	st.session_state.zoom_level = int(-1.2*st.session_state.slider_dist/100 + 11)

	if not df is None:
		map = leafmap.Map(
			center = st.session_state.map_center,
			zoom = st.session_state.zoom_level,
			fullscreen_control = False,
			draw_control = False,
			measure_control = False,
			search_control = False,
			)
		df['place_title'] = '<b>' + df['name'] + '</b>'
		# df['contact'] = df.apply(
		# 	lambda x: x['website'] if x['website'] != 0 and x['website'] != '0'
		# 				else "https://www.google.com/search?q=" + urllib.parse.quote(x['name']), 
		# 				axis=1
		# )

		# print(df[df['index'] == 1692].head().T)

		# Build legend
		df['icon'] = df['icon'].apply(lambda x: 'location-pin' if x == 0 else x)
		df_legend = df[['legend', 'icon']].drop_duplicates().sort_values(by='legend')

		legend = ''
		if df_legend.shape[0] <= 10:
			legend_activities = ""
			for i, row in df_legend.iterrows():
				legend_activities += '<a style="color:#ffffff;font-size:100%;margin-left:10px;"><i class="fa fa-' + row['icon'] + '"></i>&nbsp;&nbsp;' + row['legend'] + ''

			# legend_height = 10 + df_legend.shape[0]*18
			legend_height = 20
			legend_width = df_legend.shape[0]*100
			legend_html = '''
				{% macro html(this, kwargs) %}
				<div style="
					position: fixed; 
					bottom: 20px;
					right: 10px;
					width: ''' + str(legend_width) + '''px;
					height:''' + str(legend_height) + '''px;
					z-index:9999;
					font-size:12px;
					">''' + legend_activities + '''
				</div>
					<div style="
					position: fixed; 
					bottom: 20px;
					right: 10px;
					width: ''' + str(legend_width) + '''px;
					height:''' + str(legend_height) + '''px;
					z-index:9998;
					font-size:12px;
					background-color: ''' + pc + ''';
					opacity: 0.7;
					">
				</div>
				{% endmacro %}
				'''
			
			legend = branca.element.MacroElement()
			legend._template = branca.element.Template(legend_html)

		# print(df[["phone", "email"]].head())

		for i, row in df.iterrows():
			icon_type = row['icon']
			# print('icon_type', icon_type)

			icon = plugins.BeautifyIcon(
								icon = icon_type,
								# icon_shape = "marker",
								border_color = 'white',
								text_color = "#ffffff",
								background_color = pc,
								fill_opacity=0.7,
							)
			popup_txt = ('<a href=' + 
							str(row['contact']) + ' target="_new">' + 
							row['place_title'] + '</a>' + 
							# row['getdirections'] + 
							'<br>' + row[col_tags] + '<br>' + 
							(("phone: " + str(row['phone'])) if str(row['phone']) != "0" else "") + '<br>' + 
							(("email: " + str(row['email'])) if str(row['email']) != "0" else "")
			)

			if len(st.session_state.show_onmap) > 0:
				show_popup = is_sticky = True if row['index'] in st.session_state.show_onmap else False
			else:
				show_popup = is_sticky = False
			
			marker = folium.Marker(
				location=(row['latitude'], row['longitude']),
				popup = folium.Popup(popup_txt, min_width=200, max_width=200, show=show_popup, sticky=is_sticky),
				icon = icon,
				# layer_name="Marker Cluster",
			)
			marker.add_to(map)
		
		# print('map=', map)
		# marker_cl.add_child(marker)

		folium.LayerControl().add_to(map)
		if legend != '':
			map.get_root().add_child(legend)


		return map
	else:
		return None


def create_icon_list():
	ref_activities = pd.read_csv(f'{syst}/data/ref_activity_v1.csv')
	dict_icon_categ = dict(zip(ref_activities[col_category], ref_activities['category_icon']))
	dict_icon_activ = dict(zip(ref_activities[col_activity], ref_activities['activity_new_icon']))
	st.session_state.icon_dict = {**dict_icon_activ, **dict_icon_categ}
	return ref_activities


@st.cache_data()
def prep_city():
	ref_cities = pd.read_csv(f'{syst}/data/ref_city.csv', encoding='latin-1')
	return ref_cities


@st.cache_data()
def prep_data():
	ref_activities = create_icon_list()
	places = pd.read_csv(f'{syst}/data/indices.csv')
	tmp = ref_activities.merge(places, on=['index'], how='inner')
	places_categ = tmp[tmp[col_super_category] != val_others]
	distances = pd.read_csv(f'{syst}/data/distances.csv').drop(columns=['name'])
	return places_categ, distances

def read_data(activity, city):
	_tmp0, _dist = prep_data()
	_tmp = _tmp0.merge(_dist[_dist['city'] == city], left_on=['index'], right_on=['place_idx'])
	if activity == all_option and st.session_state.search_k == search_empty_text:
		full_list = list(_tmp[col_activity].unique())
		df = _tmp[(_tmp[col_activity].isin(full_list))]
		df['activity'] = df[col_activity]
		df.rename(columns={'activity_new_icon': 'icon'}, inplace=True)
	else:
		# almost sure if a super-category
		full_list = list(_tmp[_tmp[col_super_category] == activity][col_category].unique())
		df = _tmp[_tmp[col_category].isin(full_list)]
		df.rename(columns={col_category:'activity', 'category_icon': 'icon'}, inplace=True)
	full_list.sort()
	st.session_state.map_full = full_list
	df = df.sort_values(by='activity')
	return df
	

def filt_data(activity):
	df = read_data(activity, city=st.session_state.selectbox_city)

	# Filter by distance
	if 'slider_dist' in st.session_state:
		dist_thresh = st.session_state.slider_dist
	else:
		dist_thresh = slider_traveltime_max
	df = df[df['time_min'] <= dist_thresh]

	if df.shape[0] > 0:
		map_full = st.session_state.map_full
		# each element in map_filt_single is in map_full
		isin_map_full = False
		if 'map_filt_single' in st.session_state and len(st.session_state.map_filt_single) > 0:
			isin_map_full = max([el in map_full for el in st.session_state.map_filt_single])
		
		map_filt = (st.session_state.map_filt_single 
	      if 'map_filt_single' in st.session_state 
				and st.session_state.map_filt_single != st.session_state.first_option
				and isin_map_full
				else map_full)
		
		# print('map_full: ', map_full)
		# print('map_filt:', map_filt)
		
		df['place_title'] = '<b>' + df['name'] + '</b>'
		df['contact'] = df.apply(
			lambda x: x['website'] if pd.notnull(x['website']) 
						else "https://www.google.com/search?q=" + urllib.parse.quote(x['name']), 
						axis = 1)

		df_filt = df[df['activity'].isin(map_filt)].sort_values(by='activity').fillna(0)
		if df_filt.shape[0] > 0:
			df_filt['activity_en_new_max'] = df_filt[col_activity]
			df_filt_agg = df_filt
			if st.session_state.icon_dict == {}:
				create_icon_list()

			icon_dict = st.session_state.icon_dict
			df_filt_agg['legend'] = df_filt_agg['activity']
			df_filt_agg['icon'] = df_filt_agg.apply(lambda x: icon_dict.get(x['legend'], 'location-pin'), axis = 1)
			return df_filt_agg.sort_values(by='num_reviews', ascending=False).head(500)
		else:
			map_full = []
			map_filt = []
			return pd.DataFrame()
	else:
		map_full = []
		map_filt = []
		return pd.DataFrame()
	
if __name__ == "__main__":	
	main()

	
