#!/bin/bash

# Define variables
source_folder="/home/pi/FanController/.node-red"
link_destination="/home/pi/.node-red"

# Check if the source folder exists
if [ -d "$source_folder" ]; then

    # Check if the destination exists
    if [ -e "$link_destination" ]; then
	# Check if it's a symbolic link
	if [ -L "$link_destination" ]; then
	    # Remove the existing symbolic link
	    rm "$link_destination"
	    echo "Existing symbolic link removed."
	else
	    # Remove the existing regular file or directory
	    rm -r "$link_destination"
	    echo "Existing file or directory removed."
	fi
    fi


    # Create the new symbolic link
    ln -s "$source_folder" "$link_destination"
    echo "New symbolic link created successfully."
else
    echo "Error: Source folder does not exist. Please make sure the folder exists before creating a link."
fi
