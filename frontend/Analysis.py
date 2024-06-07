import os
import random
import string
import streamlit as st
from backend.Steganography_img import decode as decode_image
from backend.Steganography_sound import decode_audio


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
            type=['.jpg', '.png', '.mp4', '.mov', 'wav'],
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
            elif media_file.type == 'audio/mpeg' or  media_file.type == 'audio/wav':
                st.audio(media_file_data)
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
                            
                status_message = st.empty()
                
                # Get parent directory
                parent_directory = os.path.dirname(os.path.dirname(__file__))
                # Get random string for file name
                random_string = generate_random_string()
                 # Saving original file extention
                original_extension = os.path.splitext(media_file.name)[1]
                # Path to Media/Steganalysis folder 
                save_analysis_path = os.path.join(parent_directory, "Media/Steganalysis", f"{random_string}{original_extension}")

                # Ensure the directory exists
                os.makedirs(os.path.dirname(save_analysis_path), exist_ok=True)

                try:
                    # Save the uploaded image
                    with open(save_analysis_path, "wb") as f:
                        f.write(media_file_data)

                    if os.path.exists(save_analysis_path):
                        try:
                            status_message.write("Starting decode process...")

                            new_lsb = 0

                            decoded_text = decoding(media_file, media_file_data, save_analysis_path, lsb_selected_int)
                            
                            # Check if decoded_text is None and perform recursive decoding
                            if decoded_text is None or lsb_selected_int == 0: 
                                new_lsb = 1
                                while new_lsb <= 8 and decoded_text is None:
                                    status_message.write(f"Attempting to decode with {new_lsb} LSB")
                                    decoded_text = decoding(media_file, media_file_data, save_analysis_path, new_lsb)
                                    new_lsb += 1

                            status_message.write("Decoding completed!")
                            
                            if new_lsb >= 8 and decoded_text is None:
                                st.write("Unable to decode message.")
                            else:
                                st.write("The secret message is:")
                                st.write(decoded_text)
                            
                        except Exception as e:
                            st.error(f"An error occurred during decoding: {e}")
                    else:
                        st.error(f"File does not exist at path: {save_analysis_path}")

                except Exception as e:
                    st.error(f"An error occurred during saving: {e}")

def decoding(media_file, media_file_data, save_path, lsb):
    decoded_text = None

    if media_file.type == 'image/jpeg' or media_file.type == 'image/png':
        decoded_text = decode_image(save_path, lsb)

    elif media_file.type == 'video/quicktime' or media_file.type == 'video/mp4':
        st.video(media_file_data)

    elif media_file.type == 'audio/mpeg' or  media_file.type == 'audio/wav':
        decoded_text = decode_audio(save_path, lsb)
        
    return decoded_text