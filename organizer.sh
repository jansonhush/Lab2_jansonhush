#!/bin/bash

SOURCE_FILE="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

# Checking file to archive exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: '$SOURCE_FILE' not found in $(pwd). Nothing to archive." >&2
    exit 1
fi

# 2. Create the archive directory if it does not exist
if [ ! -d "$ARCHIVE_DIR" ]; then
    if ! mkdir "$ARCHIVE_DIR"; then
        echo "Error: could not create directory '$ARCHIVE_DIR'." >&2
        exit 1
    fi
    echo "Created directory: $ARCHIVE_DIR"
fi

# 3. Build the timestamped name, e.g. grades_20251105-170000.csv
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

# 4. Move (rename) the file into the archive
if ! mv "$SOURCE_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME"; then
    echo "Error: could not move '$SOURCE_FILE' to '$ARCHIVE_DIR/'." >&2
    exit 1
fi

# 5. Workspace reset: create a new, empty grades.csv
: > "$SOURCE_FILE"

# 6. Append the details to the log (accumulates across runs)
echo "[$TIMESTAMP] Archived '$SOURCE_FILE' -> '$ARCHIVE_DIR/$ARCHIVED_NAME'" >> "$LOG_FILE"

echo "Archived '$SOURCE_FILE' as '$ARCHIVE_DIR/$ARCHIVED_NAME'."
echo "Created a new empty '$SOURCE_FILE'. Logged to '$LOG_FILE'."