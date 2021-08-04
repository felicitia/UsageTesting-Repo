## Running for a usage
1. `root_usage_dir` should point to V2S's results of a usage, e.g., "Combined/SignIn/"
2. run `1_step_extraction/step_extraction.py` to generate `clicked_frames` folder
3. go to `binaryClassifier` and follow README to generate final `typing_result.csv`
4. run `1_step_extraction/step_cleaning.py` to generate `steps_clean` folder (check if it contains extra steps like outside of the app)
5. run `1_step_extraction/special_step_recognition.py` to append special actions in `steps_clean` folder
6. run `2_ir_classification/screen_widget_extraction.py` (comment out extract_widget function) to generate `ir_data_auto` folder with screens only
7. get UIED results (run UIED v2.3's `run_mybatch.py`) -- check terminal for running time as this process is time-consuming
8. run `2_ir_classification/screen_widget_extraction.py` (comment out extract_screen function) to add widget crops to `ir_data_auto` folder (check if each screen has a matching widget.jpg. function in `util_func.py`)

## Setting up LS (run on the LS server)
1. download your data on the LS server
2. go to `2_ir_classification` folder and run `python create_symlink.py` (need to change `usage_root_dir`) — this should create a symlink under the same folder called `sym_...` with many .jpg files inside, e.g., `sym_video_data_examples`
3. same directory, run `./serve_local_files.sh {you symlink folder} '*.jpg'` (e.g., `./serve_local_files.sh sym_video_data_examples/ '*.jpg'`) — this should start a server at port 8081 with images uploaded (as a sanity check, you can go to your browser to see if the image is loaded (e.g., http://localhost:8081/etsy-signin-1-bbox-1127-widget.jpg). leave this server running during your entire labeling process.
4. same directory, run `python generate_import_data.py` (need to change `image_root_dir` and `server_addr`) — this should generate a file called `import_....json`, e.g., `import_video_data_examples.json`
5. go to your LS project and import data by uploading the json file generated above

## Running UIED v2.3
1. `ImportError: No module named 'detect_text_east.lib_east.lanms.adaptor’` — check this [thread](https://github.com/argman/EAST/issues/174). Replace the Makefile in `/detect_text_east/lib_east/lanms` and go to that directory to run `make` command.

## Missing Usages

### Shopping Apps
1. "Address" usage: **Etsy**, **Groupon**, and **Geek** don't have this feature. You can skip it.
2. "Filter" usage: **Home**, and **Wish** don't have this feature. You can skip it.
3. "AddCart" and "RemoveCart" usages: 
**5Miles** doesn't have shopping cart, so please use "likes" in 5Miles as the shopping cart, e.g., for the "AddCart" usage, you can add the item to the "likes";
**Groupon** doesn't have "AddCart", so please click the heart to add the item to "saved" instead
4. "Terms" usage: **Zappos** doesn't have it. You can skip it.

### News Apps
1. "Sign In" and "Account" usages: **ABC**, **USA Today**, **BBC**, **Reuters**, **CBS** don't have them, and **Fox News** needs TV provider. You can skip.
2. "Textsize": **USA Today** doesn't have it. You can skip it.
3. "AddBookmark" and "RemoveBookmark": **BBC** doesn't have it. You can skip it.
4. "Help" and "Contact": **Buzzfeed** doesn't have it. Click "Send Feedback" instead. 
5. "Search": **News Break** doesn't have it. You can skip it.

## Changing Apps due to version compatibility
1. Ebay's version is changed (updated the version and used Git LFS to store due to its large size)
