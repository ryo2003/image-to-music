import streamlit as st

ai_page = st.Page(page="pages/soundraw.py", title="AI", icon=":material/home:")
spotify_page = st.Page(page="pages/spotify.py", title="Spotify", icon=":material/home:")
pg = st.navigation([ai_page,spotify_page])
pg.run()