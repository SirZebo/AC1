import streamlit as st
from Analysis import analysis
from Steganography import steganography

def main():
    st.set_page_config(
        page_title="steganography",
        layout="wide"
    )

    st.sidebar.title('Steganographer')

    page = st.sidebar.radio(
        label="Navigation", 
        options=["Steganography", "Analysis"],
        label_visibility="collapsed"
    )

    if page == "Steganography":
        steganography()
    elif page == "Analysis":
        analysis()

if __name__ == '__main__':
    main()