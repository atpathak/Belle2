for i in `seq -w 1 26`
do
cat Summary_only8_28Jun.txt | grep 2019/06/${i} | sed -e 's/,/ /g' | awk '{ if ($NF>1000000) {print $1, $2, $3, $4} }' | tee 2019_06_${i}_1M.txt 
done

