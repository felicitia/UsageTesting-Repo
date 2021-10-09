import os, shutil, csv, json

usage_root_dir = "C:/Users/leony/Downloads/Combined"

templist = []
screen_list = []
widget_list = []

folders = [folder for folder in os.listdir(usage_root_dir) if os.path.isdir(os.path.join(usage_root_dir, folder)) and not folder.startswith('.')]

for folder in folders:

    with open("importData_temp.json", 'w+') as temp:

        dir_to_csv = usage_root_dir + "/" + folder + "/LS-annotations.csv"
        dir_to_json = usage_root_dir + "/" + folder + "/import_" + folder.split("-")[1] + ".json"

        with open(dir_to_csv, newline='') as csvfile:
            annotations = csv.reader(csvfile)

            for row in annotations:
                if row == ['screen', 'widget', 'id', 'tag_screen', 'tag_widget', 'annotator', 'annotation_id']:
                    row = None
                    continue

                item = row[0]
                screen = row[3]
                widget = row[4]
                screen_list.append(screen)
                widget_list.append(widget)

                file = open(dir_to_json,)
                data = json.load(file)
                for line in data:
                    if item in line["data"]["screen"]:
                        line["annotations"] = \
                            [{"result": [{"value": {"choices": [screen]}, "from_name": "tag_screen", "to_name": "screen", "type": "choices"}, \
                                {"value": {"choices": [widget]}, "from_name": "tag_widget", "to_name": "widget", "type": "choices"}]}]
                        templist.append(line)

                file.close()

        json.dump(templist, temp, indent=4)
        templist = []
    
    os.replace("importData_temp.json", dir_to_json)

    print("Finished "+folder)


print("Done!")

print({i:screen_list.count(i) for i in screen_list})
print({i:widget_list.count(i) for i in widget_list})
screen_list = set(screen_list)
print("count of screens: "+str(len(screen_list)))
widget_list = set(widget_list)
print("count of widgets: "+str(len(widget_list)))