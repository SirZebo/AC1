import streamlit as st
from Analysis import analysis
from Steganography import steganography

def main():
    st.set_page_config(
        page_title="steganography",
        layout="wide"
    )

    st.sidebar.title('Steganographer')


    st.markdown(
    """
    <style>
    .sidebar .widget-title {
        display: none;  /* Hide the title of the radio button */
    }
    .sidebar .stRadio > label {
        display: block;
        margin-bottom: 10px;
        cursor: pointer;
        border-radius: 5px;
        background-color: #f0f0f0;
        padding: 10px;
    }
    .sidebar .stRadio > label:hover {
        background-color: #e0e0e0;
    }
    .sidebar .stRadio > label input[type="radio"] {
        display: none;
    }
    .sidebar .stRadio > label input[type="radio"] + span {
        position: relative;
        top: 3px;
        margin-right: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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