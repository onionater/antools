mysql -uaskerry -ppassword -e "select * from FSF_rating" aesbehave | sed 's/\t/","/g;s/^/"/;s/$/"/' > tempdl.csv
