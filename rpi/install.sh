#!/bin/bash

# Default destination directory
DEST_DIR="/var/www/html/wallboard"

# Check if a destination directory was provided as an argument
if [ "$#" -ge 1 ]; then
    DEST_DIR="$1"
fi

echo "Installing wallboard templates to: $DEST_DIR"

# Ensure destination directory exists
if [ ! -d "$DEST_DIR" ]; then
    echo "Error: Destination directory $DEST_DIR does not exist."
    echo "Usage: $0 [destination_directory]"
    exit 1
fi

# Define targets as an array of strings in the format:
# "source_template : destination_filename : config_script"
TARGETS=(
    "template.html:auto.html:config.auto.js"
    # Example of adding more targets:
    # "template_video.html:video.html:config.video.js"
    # "template.html:laser.html:config.laser.js"
)

# Loop through each target
for TARGET in "${TARGETS[@]}"; do
    # Split the target string into components
    IFS=":" read -r SRC_FILE DEST_FILE CONFIG_FILE <<< "$TARGET"
    
    echo "Processing $DEST_FILE (from $SRC_FILE using $CONFIG_FILE)..."
    
    # Check if source file exists
    if [ ! -f "$SRC_FILE" ]; then
        echo "  Warning: Source file $SRC_FILE not found! Skipping..."
        continue
    fi
    
    DEST_PATH="$DEST_DIR/$DEST_FILE"
    
    # Use sudo for copy if needed, but standard cp works if you run the script as root
    cp "$SRC_FILE" "$DEST_PATH"
    if [ $? -ne 0 ]; then
        echo "  Error: Failed to copy $SRC_FILE to $DEST_PATH. Try running script with sudo."
        continue
    fi
    
    # Replace config.js with the specified config file
    # We look for src="config.js" or similar variations and replace it
    sed -i "s/src=\"config\.js\"/src=\"$CONFIG_FILE\"/g" "$DEST_PATH"
    
    # Ensure it's owned by www-data
    chown www-data:www-data "$DEST_PATH" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  Warning: Failed to chown www-data:www-data (run with sudo to fix)"
    else
        echo "  Successfully installed $DEST_FILE"
    fi
done

echo "Done!"
