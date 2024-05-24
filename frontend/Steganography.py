import streamlit as st

def main():
    st.set_page_config(
        page_title="steganography",
        layout="wide"
    )

    st.header("Steganography")

    # Create one columns
    column = st.columns([1])
    
    if "media_uploaded" not in st.session_state:
        st.session_state.media_uploaded = False

    if "payload_uploaded" not in st.session_state:
        st.session_state.payload_uploaded = False

    # UI for center column
    with column[0].container(height=900, border=False):
        st.write('**Step 1. Upload a media file**')
        media_file = st.file_uploader(
            'media', 
            type=['.jpg', '.png', '.mp4', '.mov'],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        if media_file is not None:
            st.session_state.media_uploaded = True
            media_file_data = media_file.getvalue() # Read file as bytes
            st.write("Uploaded media file: ", media_file.name)
            # st.write(media_file.type)
            if media_file.type == 'image/jpeg' or media_file.type == 'image/png':
                st.image(media_file_data)
            elif media_file.type == 'video/quicktime' or media_file.type == 'video/mp4':
                st.video(media_file_data)
            else:
                st.write("File type not supported.")
        
        st.write('**Step 2. Upload a payload file**')
        payload_file = st.file_uploader(
            'payload', 
            accept_multiple_files=False,
            label_visibility="collapsed",
            disabled=not st.session_state.media_uploaded
        )
        if payload_file is not None:
            st.session_state.payload_uploaded = True
            payload_file_data = payload_file.getvalue()
            st.write("Uploaded payload file: ", payload_file.name)

        st.write('**Step 3. Select number of LSB bits to perform Steganography**')

        st.markdown(
            """
            <style>
            .stSlider {
                max-width: 800px;  /* Adjust the max-width value as needed */
                margin: 0 auto;  /* Center the slider */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        lsb_selected = st.select_slider(
            "lsb-count",
            options=["1", "2", "3", "4", "5", "6", "7", "8"],
            label_visibility="collapsed",
            disabled=not st.session_state.payload_uploaded
        )
        
        st.write(f"Number of LSB bits selected for Steganography: {lsb_selected}")

if __name__ == '__main__':
    main()
