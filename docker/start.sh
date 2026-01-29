#!/bin/bash
set -e
source $VENV_PATH/bin/activate

# Wait for Snowstorm
until curl -sf http://snowstorm:8080/version > /dev/null; do
    sleep 5
done

    if [ "$MEDMINER_WORKFLOW" = "procedure_extraction_workflow" ]; then
    RF2_FILE=$(find /opt/snomed-data -name "*.zip" -type f | head -n 1)
    if [ -n "$RF2_FILE" ]; then
        echo "Starting SNOMED import..."
        echo "Using RF2 file: $RF2_FILE"

        # Step 1: Create import
        LOCATION=$(curl -s -i -X POST "http://snowstorm:8080/imports" \
            -H "Content-Type: application/json" \
            -d '{"branchPath":"MAIN","createCodeSystemVersion":true,"type":"SNAPSHOT"}' \
            | grep -i "^location:" | cut -d' ' -f2 | tr -d '\r\n')
        
        IMPORT_ID=$(basename "$LOCATION")
        echo "Created import with ID: $IMPORT_ID"

        # Step 2: Upload file to the import
        echo "Uploading RF2 file..."
        curl -s -X POST "http://snowstorm:8080/imports/$IMPORT_ID/archive" \
            -H "Content-Type: multipart/form-data" \
            -F "file=@$RF2_FILE"
        echo "Upload complete."



        # Wait for import to complete
        while true; do
            STATUS=$(curl -s "http://snowstorm:8080/imports/$IMPORT_ID" | jq -r '.status // "UNKNOWN"')
            echo "Import status: $STATUS"
            
            if [ "$STATUS" = "COMPLETED" ]; then
                echo "SNOMED import completed!"
                break
            fi
            
            sleep 10
        done
    fi
else
    echo "Skipping SNOMED import (only needed for procedure_extraction_workflow)"
fi

medminer extract $MEDMINER_WORKFLOW /app/data --base-dir /app/data
