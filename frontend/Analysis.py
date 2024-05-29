import os
import random
import string
import streamlit as st
from backend.Steganography_img import decode

def generate_random_string(length=8):
    """Generate a random string of letters and digits."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


def analysis():
    st.header("Analysis")

    # Create one columns
    column = st.columns([1])

    if "stego_uploaded" not in st.session_state:
        st.session_state.stego_uploaded = False

    with column[0].container(height=900, border=False):
        st.write('**Step 1. Upload a steganography file**')
        media_file = st.file_uploader(
            'media', 
            type=['.jpg', '.png', '.mp4', '.mov'],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )

        if media_file is not None:
            st.session_state.stego_uploaded = True
            media_file_data = media_file.getvalue() # Read file as bytes
            st.write("Uploaded stego file: ", media_file.name)
            if media_file.type == 'image/jpeg' or media_file.type == 'image/png':
                st.image(media_file_data, width=300)
            elif media_file.type == 'video/quicktime' or media_file.type == 'video/mp4':
                st.video(media_file_data)
            else:
                st.write("File type not supported.")

        st.write('**Step 2. If you know, select number of LSB bits to perform Steganography**')
        st.write('*If you do not, select 0.*')
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
            options=["0","1", "2", "3", "4", "5", "6", "7", "8"],
            label_visibility="collapsed",
            disabled=not st.session_state.stego_uploaded
        )

        # Ensure lsb_selected is an integer
        lsb_selected_int = int(lsb_selected)
        
        if st.session_state.stego_uploaded:
            if st.button("Perform Steganalysis"):
                
                # Get parent directory
                parent_directory = os.path.dirname(os.path.dirname(__file__))
                # Get random string for file name
                random_string = generate_random_string()
                # New filename with random string
                new_filename = f"{random_string}_{media_file.name}"
                # Path to Media/Steganalysis folder 
                save_path = os.path.join(parent_directory, "Media/Steganalysis", f"{new_filename}")
                # save_path = os.path.join(parent_directory, "Media/Steganalysis/yyinIjiq_test_11zon.png")

                # Save the uploaded image
                with open(save_path, "wb") as f:
                    f.write(media_file_data)

                if os.path.exists(save_path):
                    try:
                        st.write("Starting decode process...")
                        # Call the decode function
                        decoded_text = decode(save_path, lsb_selected_int)
                        st.write("Decoded text:")
                        st.write(decoded_text)
                    except Exception as e:
                        st.error(f"An error occurred during decoding: {e}")
                else:
                    st.error(f"File does not exist at path: {save_path}")

                 # Check if the saved media exists
                # if os.path.exists(save_path):
                #     # Check if the file is an image
                #     if media_file.type == 'image/jpeg' or media_file.type == 'image/png':
                #         decode(save_path, lsb_selected_int)
                #         st.write("done")
