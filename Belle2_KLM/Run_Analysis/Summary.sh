less export.csv | grep "New Run" | grep -v "cosmic study" | grep -v "DAQ study" | grep KLM | grep Luminosity | sed -e 's/"/,/g' | sed -e 's/;//g' | sed -e 's/,,/,/g' | awk '{print $8, $9, $12}' | sed -e 's/ /,/g' | sed 's/,/ /g' | awk '{print $1, $2, $3, $7}' | sed -e 's/ /,/g' | tee Summary.txt

