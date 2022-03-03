## Setting Up Repo for Test Generation
1. clone repo
2. install Conda environment for the project using this [environment file for Mac](https://github.com/felicitia/UsageTesting-Repo/blob/master/environment_mac.yml) or [environment file for Windows](https://github.com/felicitia/UsageTesting-Repo/blob/master/environment_windows.yml). you can use `conda env create -f environment.yml` to create the environment and activate the environment by `conda activate usage`
3. install [Appium](http://appium.io/) Desktop
4. add app's configuration in [App_Config.py](https://github.com/felicitia/UsageTesting-Repo/blob/master/code/4_dynamic_generation/App_Config.py) -- you can find relevant info in [news_app_info.csv](https://github.com/felicitia/UsageTesting-Repo/blob/master/news_app_info.csv) and [shopping_app_info.csv](https://github.com/felicitia/UsageTesting-Repo/blob/master/shopping_app_info.csv)
5. start Android Emulator (same as the one used for data collection) -- make sure the AUT (App Under Test) is installed on the Emulator, e.g., abcnews
6. start Appium Server
7. Change file paths in [global_config.py](https://github.com/felicitia/UsageTesting-Repo/blob/master/code/global_config.py) Final-Artifact can be downloaded [here](https://zenodo.org/record/5940759).
8. run main method in [dynamic_evaluation.py](https://github.com/felicitia/UsageTesting-Repo/blob/master/code/evaluation/dynamic_evaluation.py)

**Enabling REMAUI feature**
1. download [REMAUI Java program](https://drive.google.com/file/d/1787v_UKwc06yVC7XA8fh47e98PC9CPTv/view?usp=sharing)
2. install [Eclipse](https://www.eclipse.org/) for Java if you don't already have it
3. configure all the build paths (the REMAUI repo should already contain all the necessary jars except for openCV) -- see screenshots below regarding build path. you need to edit the paths of jar files to the file paths on your machine

<img width="689" alt="image" src="https://user-images.githubusercontent.com/5572614/155231533-66c8ec47-a101-4396-bfe7-95e4518b333d.png">
<img width="1007" alt="image" src="https://user-images.githubusercontent.com/5572614/155231617-2f6c6b5d-20f4-4ce2-920a-dbb5d2a20d6e.png">


4. follow this [tutorial](https://docs.opencv.org/2.4/doc/tutorials/introduction/java_eclipse/java_eclipse.html) to enable openCV (see notes below first if using Mac)
5. run the main method in `edu.wm.cs.semeru.redraw.REMAUI` through Eclipse's "run configurations" and give one argument which is the path of a screen image (see below). (Make sure to change file path in `run_REMAUI_single_image` function, including `projectRootDirectory`, and `screenshots` String which should be the folder name that contains the image). REMAUI output should be in the parent folder of the image path. 
6. After running sccessfully, copy the command and replace `REMAUI_cmd` in [state.py](https://github.com/felicitia/UsageTesting-Repo/blob/master/code/4_dynamic_generation/state.py)

If you're using Mac, you need to build openCV yourself in order to have that "build" folder. follow steps below:
1. after downloading openCV's source, make a `build` directory in it. 
2. then you build opencv using cmake command. If you are in the build folder you just created, `cmake ..` will do. Then run `make -j8`
3. from the tutorial above, you should put `build/lib` as the native library location

<img width="979" alt="image" src="https://user-images.githubusercontent.com/5572614/155193946-3e197870-2ebc-46ba-b1c1-b5942fe49b3e.png">

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

## Running V2S on Gypsum
1. copy videos to scrtach, e.g., `rsync -av . gypsum-remote:/mnt/nfs/scratch1/yixuezhao/v2s_input/summer_data`
2. go to `code/v2s_optimized` to generate JSON v2s batch config files (can be done on gypsum in `work1/brun/yixuezhao/video2scenario/myscripts`) and run `generate_v2s_config.py`
3. check gypsum's status (`sinfo` command) and pick the idle cluster to use. sample .sh script can be found in `code/scripts`
4. `conda activate python_v2s` and run .sh script on gypsum using `sbatch` command

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
