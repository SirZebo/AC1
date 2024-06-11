import os
import random
import string
import cv2
import streamlit as st
from streamlit_extras.app_logo import add_logo
from backend.Steganography_img import encode as encode_image
from backend.Steganography_sound import encode_audio
from backend.videostego import encode_video_with_audio  # Import the new function
from backend.zip import zipSecretFile


def generate_random_string(length=8):
    """Generate a random string of letters and digits."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def steganography():

    # Get parent directory
    parent_directory = os.path.dirname(os.path.dirname(__file__))
    # Get random string for file name
    random_string = generate_random_string()

    # Create one column
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
            type=['.jpg', '.png', '.mp4', '.mov', 'wav'],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        if media_file is not None:
            st.session_state.media_uploaded = True
            media_file_data = media_file.getvalue()  # Read file as bytes
            st.write("Uploaded media file: ", media_file.name)
            st.write(media_file.type)
            if media_file.type == 'image/jpeg' or media_file.type == 'image/png':
                st.image(media_file_data, width=300)
            elif media_file.type == 'video/quicktime' or media_file.type == 'video/mp4':
                st.video(media_file_data)
            elif media_file.type == 'audio/mpeg' or media_file.type == 'audio/wav':
                st.audio(media_file_data)
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

            # Saving original file extension
            original_extension = os.path.splitext(payload_file.name)[1]
            payload_filename = f"{random_string}{original_extension}"
            payload_file_path = os.path.join(parent_directory, "Media/Raw", payload_filename)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(payload_file_path), exist_ok=True)

            with open(payload_file_path, "wb") as f:
                f.write(payload_file_data)
            st.write("Uploaded payload file:", payload_file.name)

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

        # Ensure lsb_selected is an integer
        lsb_selected_int = int(lsb_selected)

        if st.session_state.payload_uploaded:
            st.write(f"Number of LSB bits selected for Steganography: {lsb_selected}")

        if st.session_state.media_uploaded & st.session_state.payload_uploaded:
            
            if st.button("Perform Steganography"):
                try:
                    status_message = st.empty()  # Create a placeholder for the status message

                    # Saving original file extension
                    original_extension = os.path.splitext(media_file.name)[1]
                    # New filename with random string
                    new_filename = f"{random_string}{original_extension}"
                    # Path to Media/Raw folder 
                    save_path = os.path.join(parent_directory, "Media/Raw", f"{new_filename}")

                    # Ensure the directory exists
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    # Save the uploaded image
                    with open(save_path, "wb") as f:
                        f.write(media_file_data)

                    # Check if the saved media exists
                    if os.path.exists(save_path):

                        status_message.write("Starting encode process...")

                        # Check if the file is an image
                        if media_file.type == 'image/jpeg' or media_file.type == 'image/png':

                            zippedPayload_file_path = zipSecretFile(payload_file_path)
                            # Conduct stego on image
                            encoded_image = encode_image(zippedPayload_file_path, save_path, lsb_selected_int)
                            # Path to Media/Stego folder
                            save_stego_path = os.path.join(parent_directory, "Media/Steganography", f"{random_string}.png")
                            
                            # Ensure the directory exists
                            os.makedirs(os.path.dirname(save_stego_path), exist_ok=True)

                            # Save encoded image to folder
                            cv2.imwrite(save_stego_path, encoded_image)
                            st.image(save_stego_path, caption='Image after conducting Steganography.', width=300)

                            with open(save_stego_path, "rb") as f:
                                st.download_button(

                                    label="Download stego file",

                                    data=f,

                                    file_name=os.path.basename(save_stego_path),

                                    mime="application/octet-stream"

                                )


                        elif media_file.type == 'video/quicktime' or media_file.type == 'video/mp4':
                            
                            output_mp4_path = os.path.join(parent_directory, "Media/Steganography", f"{random_string}.mp4")
                            os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
                            
                            encode_video_with_audio(save_path, payload_file_path, output_mp4_path, lsb_selected_int)
                            
                            st.video(output_mp4_path)
                            
                            with open(output_mp4_path, "rb") as f:
                                st.download_button(

                                    label="Download stego file",

                                    data=f,

                                    file_name=os.path.basename(output_mp4_path),

                                    mime="application/octet-stream"

                                )

                        
                        elif media_file.type == 'audio/mpeg' or  media_file.type == 'audio/wav':
                            zippedPayload_file_path = zipSecretFile(payload_file_path)
                            stegoAudio_path = encode_audio(zippedPayload_file_path, save_path, lsb_selected_int)
                            st.audio(media_file_data)
                            with open(stegoAudio_path, "rb") as f:
                                st.download_button(

                                    label="Download stego file",

                                    data=f,

                                    file_name=os.path.basename(stegoAudio_path),

                                    mime="application/octet-stream"
                                )

                        status_message.write("Encoding completed!")
                    else:
                        st.write("Error: Saved media not found.")
                except Exception as e:
                    st.write("Error: "+ str(e))