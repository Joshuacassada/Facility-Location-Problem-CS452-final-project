#!/bin/bash

###############################################
# CONFIG — EDIT THESE IF NEEDED
###############################################

LOWER_BOUND_TIMEOUT=2
APPROX1_TIME=1        # INTERNAL time limit passed as -t to approx solver
EXACT_TIMEOUT=20      # Shell timeout for exact solver

LOWER_BOUND_CMD="python3 ../lower_bound.py"
APPROX1_CMD="python3 ../../dustin_approx_sol/facility_location_approx.py"
EXACT_CMD="python3 ../../exact_solution/facility_location_exact.py"

TEST_DIR="."
PREFIX="test_case_"
SUFFIX=".txt"
START=1
END=50

OUTPUT_FILE="../results.csv"
COST_PARSER="../compute_cost_from_output.py"
###############################################


# CSV header
echo "test_case,lower_bound,approx1,exact" > "$OUTPUT_FILE"

echo "Running all test cases..."
echo "-------------------------------------------"


for ((i=$START; i<=$END; i++)); do
    FILE="$TEST_DIR/${PREFIX}${i}${SUFFIX}"

    if [[ ! -f "$FILE" ]]; then
        echo "Skipping missing file: $FILE"
        continue
    fi

    echo "→ Test case $i"


    ##########################
    # LOWER BOUND
    ##########################
    LB=$(timeout $LOWER_BOUND_TIMEOUT $LOWER_BOUND_CMD "$FILE" 2>/dev/null)
    [[ -z "$LB" ]] && LB="ERR"


    ##########################
    # APPROX
    ##########################
    A1_OUT="tmp_a1_$i.txt"

    $APPROX1_CMD -t "$APPROX1_TIME" "$FILE" > "$A1_OUT" 2>/dev/null
    EXIT_CODE=$?

    if [[ $EXIT_CODE -ne 0 ]]; then
        A1="ERR"
    else
        # Count number of opened facility IDs (e.g., F1, F5,...)
        A1=$(grep -o "F[0-9]\+" "$A1_OUT" | wc -l)
        [[ $A1 -eq 0 ]] && A1="ERR"
    fi


    ##########################
    # EXACT SOLVER
    ##########################
    EX_OUT="tmp_ex_$i.txt"

    timeout $EXACT_TIMEOUT \
        $EXACT_CMD "$FILE" \
        > "$EX_OUT" 2>/dev/null

    if [[ $? -eq 124 ]]; then
        EX="TIMEOUT"
    else
        EX=$(grep -o "F[0-9]\+" "$EX_OUT" | wc -l)
        [[ $EX -eq 0 ]] && EX="ERR"
    fi



    ##########################
    # WRITE CSV
    ##########################
    echo "$i,$LB,$A1,$EX" >> "$OUTPUT_FILE"


    ##########################
    # CLEAN TMP FILES
    ##########################
    rm -f "$A1_OUT"
    rm -f "$EX_OUT"

done


echo "-------------------------------------------"
echo "Done! Results saved to $OUTPUT_FILE"
