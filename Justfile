
run:
 rm -f out.json
 scrapy runspider blueroom.py --out out.json
 python post_process.py
 python validate.py
