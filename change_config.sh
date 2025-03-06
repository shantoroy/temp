#!/bin/bash

# Define environment options
declare -A ENV_PATHS
ENV_PATHS["1"]="/app/env/dev"
ENV_PATHS["2"]="/app/env/stage"
ENV_PATHS["3"]="/app/env/prod"

declare -A ENV_NAMES
ENV_NAMES["1"]="dev"
ENV_NAMES["2"]="stage"
ENV_NAMES["3"]="prod"

# Prompt for environment selection
echo "Select Environment:"
echo "1) dev"
echo "2) stage"
echo "3) prod"
read -p "Enter the number corresponding to the environment: " env_choice

# Validate selection
if [[ -z "${ENV_PATHS[$env_choice]}" ]]; then
    echo "Invalid choice. Exiting."
    exit 1
fi

ENV_DIR="${ENV_PATHS[$env_choice]}"
ENV_NAME="${ENV_NAMES[$env_choice]}"

# Prompt for file selection
echo "Select a file to edit:"
echo "1) test1.txt"
echo "2) test2.txt"
read -p "Enter the number corresponding to the file: " file_choice

case $file_choice in
    1) FILE_NAME="test1.txt" ;;
    2) FILE_NAME="test2.txt" ;;
    *) echo "Invalid file choice. Exiting."; exit 1 ;;
esac

FILE_PATH="$ENV_DIR/$FILE_NAME"

# Ensure the file exists
if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File '$FILE_PATH' not found!"
    exit 1
fi

# Create a backup before making changes
DATE=$(date +"%Y-%m-%d")
BACKUP_FILE="/tmp/${ENV_NAME}_${FILE_NAME}_${DATE}.bak"
cp "$FILE_PATH" "$BACKUP_FILE"

echo "Backup created at: $BACKUP_FILE"

# Main loop to choose between parameter update or string replacement
while true; do
    echo "Choose an option:"
    echo "1) Change parameter value (key=value)"
    echo "2) Replace a string"
    echo "q) Quit"
    read -p "Enter your choice: " action_choice

    case $action_choice in
        1)  # Change parameter value
            while true; do
                read -p "Enter the parameter key to update (or 'q' to stop): " param_key
                [[ "$param_key" == "q" ]] && break

                read -p "Enter the new value for '$param_key': " param_value

                # Using sed to update parameter value
                sed -i "s|^$param_key=.*|$param_key=$param_value|" "$FILE_PATH"
                echo "Updated '$param_key' to '$param_value' in $FILE_PATH"
            done
            ;;
        2)  # Replace a string
            while true; do
                read -p "Enter the old string to replace (or 'q' to stop): " old_str
                [[ "$old_str" == "q" ]] && break

                read -p "Enter the new string: " new_str

                # Using sed to replace all occurrences
                sed -i "s|$old_str|$new_str|g" "$FILE_PATH"
                echo "Replaced '$old_str' with '$new_str' in $FILE_PATH"
            done
            ;;
        q)  # Quit the script
            echo "Exiting script."
            exit 0
            ;;
        *) 
            echo "Invalid choice. Please enter 1, 2, or q."
            ;;
    esac
done
