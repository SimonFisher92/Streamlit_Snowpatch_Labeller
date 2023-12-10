import os
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(layout="wide")
s1, s2 = st.columns(2)

data_repo = 'data_repo'

# Create the patch dict from the data repo
patch_dict = {}
for patch in os.listdir(data_repo):
    patch_dict[patch] = []
    for img in os.listdir(os.path.join(data_repo, patch)):
        if img.endswith('.png') and not os.path.exists(os.path.join(data_repo, patch, 'GT', img)):
            patch_dict[patch].append(os.path.join(data_repo, patch, img))

# Callback to reset session state
def reset_state():
    st.session_state.img_index = 0
    st.session_state.remaining_images = len(patch_dict[patch_choice])
    st.session_state.clicked = False
    #update_progress()

# Update progress bar and text
# def update_progress():
#     total_images = len(patch_dict[patch_choice])
#     progress_bar.progress((total_images - st.session_state.remaining_images) / total_images)
#     progress_text.markdown(f"Remaining: {st.session_state.remaining_images} images")

# Sidebar selection for patches
patch_choice = st.sidebar.selectbox('Select patch', list(patch_dict.keys()), on_change=reset_state)
img_list = patch_dict[patch_choice]

st.sidebar.markdown(f"{len(img_list)} images remaining in {patch_choice}")

# Initialize session state variables
if 'img_index' not in st.session_state:
    st.session_state.img_index = 0
if 'remaining_images' not in st.session_state:
    st.session_state.remaining_images = len(img_list)
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

# Initialize progress bar and text
# progress_bar = st.sidebar.progress(0)
# progress_text = st.sidebar.markdown("Remaining: 0 images")
#update_progress()

# Define button click action
def click_button():
    st.session_state.clicked = True
    next_index = st.session_state.img_index + 1
    st.session_state.img_index = next_index if next_index < len(img_list) else 0
    if st.session_state.remaining_images > 0 and next_index < len(img_list):
        st.session_state.remaining_images -= 1
    #update_progress()
    plt.clf()
    plt.cla()
    plt.close()
    st.empty()

stroke_width = st.sidebar.slider("Stroke width: ", 1, 8, 3)
st.button('Next image', on_click=click_button)


if st.session_state.clicked and img_list and st.session_state.img_index < len(img_list):
    img_name = img_list[st.session_state.img_index]
    img = Image.open(img_name)
    with s1:
        # Create a canvas component
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color='black',
            background_color='white',
            background_image=img,
            update_streamlit=True,
            height=img.height,
            width=img.width,
            drawing_mode='freedraw',
            point_display_radius=0,
            key="canvas",
        )

    if canvas_result.json_data is not None:
        fig, ax = plt.subplots()
        for obj in canvas_result.json_data['objects']:
            if obj['type'] == 'path':
                path_data = obj['path']
                polygon_points = [tuple(point[1:3]) for point in path_data if point[0] != 'M']
                polygon_points = [[x, y] for x, y in polygon_points]
                polygon = patches.Polygon(polygon_points, closed=True, color='red')
                ax.add_patch(polygon)

        ax.set_xlim(0, img.width)
        ax.set_ylim(0, img.height)
        ax.invert_yaxis()
        ax.set_axis_off()
        ax.imshow(img)


        with s2:
            st.pyplot(fig)

if st.button('Save Annotation'):
    if 'fig' in locals():

        if not os.path.exists(os.path.join(data_repo, patch_choice, 'GT')):
            os.makedirs(os.path.join(data_repo, patch_choice, 'GT'))

        save_filename = os.path.join(data_repo, patch_choice, 'GT', os.path.basename(img_name))


        fig.savefig(save_filename, bbox_inches='tight', pad_inches=0, dpi=211.2)
        plt.clf()
        plt.cla()
        plt.close()
        st.empty()
        st.session_state.clicked = False

