import streamlit as st
import app1
import app2
import requests
from PIL import Image

# Init apps
PAGES = {
    "Player bar chart": app1,
    "Player comparator": app2
}

hide_footer_style = """
<style>
.reportview-container .main footer {visibility: hidden;}    
"""
st.markdown(hide_footer_style, unsafe_allow_html=True)

# Sidebar with apps selection
logo = Image.open(requests.get('https://raw.githubusercontent.com/DunkTheData/FootballCharts/main/img/logo.PNG',
                               stream=True).raw)
st.sidebar.image(logo, use_column_width=True)

st.sidebar.title('Applications')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]

st.sidebar.write("Twitter: [@DunkTheData](https://twitter.com/DunkTheData)")

# Footer
footer = """<style>
img {
  width: 150px;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Data:</p>
<img id="footer" src="https://d2p3bygnnzw9w3.cloudfront.net/req/202109021/logos/fb-logo.svg">
<img id="footer" src="https://d2p3bygnnzw9w3.cloudfront.net/req/202109021/images/klecko/statsbomb.png">
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

page.app()
