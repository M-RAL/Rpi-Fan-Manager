#!/bin/bash

# Define variables
source_folder="/home/pi/FanController/services"
file_name="FanController_mqtt.service"
link_destination="/etc/systemd/system/$file_name"

# Check if the source file exists
if [ -f "$source_folder/$file_name" ]; then
    
    # Check if the symbolic link already exists
    if [ -L "$link_destination" ]; then
        # Ask the user if they want to overwrite the existing link
        read -p "Symbolic link already exists. Do you want to overwrite it? (y/n): " overwrite_link

        if [ "$overwrite_link" == "y" ]; then
            # Remove the existing symbolic link
            sudo rm "$link_destination"
            echo "Existing symbolic link removed."
        else
            echo "Script aborted. No changes made."
            exit 0
        fi
    fi
    
    # Create the symbolic link
    sudo ln -s "$source_folder/$file_name" "$link_destination"
    echo "Symbolic link created successfully."
    
    # Ask the user if they want to enable and start the service
    read -p "Do you want to enable and start the service? (y/n): " enable_service
    if [ "$enable_service" == "y" ]; then
        # Enable and start the service
        sudo systemctl enable "$file_name"
        sudo systemctl start "$file_name"
        echo "Service enabled and started."
    else
        echo "Service not enabled and started. You can manually enable and start it later."
    fi
    
else
    echo "Error: Source file does not exist. Please make sure the file exists before creating a link."
fi

