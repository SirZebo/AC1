import streamlit as st
from frontend.Analysis import analysis
from frontend.Steganography import steganography

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
        st.header("Steganography")
        steganography()
    elif page == "Analysis":
        analysis()

if __name__ == '__main__':
    main()