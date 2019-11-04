for i in `seq -w 24 29`
do
cat Summary.txt | grep 2019/09/${i} | sed -e 's/,/ /g' | awk '{print $1, $2, $3, $4}' | tee 2019_09_${i}_1M.txt 
done

