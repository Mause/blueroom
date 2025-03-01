all: output/blueroom.org.au.ics output/ourgoldenage.com.au.ics output/dates.ics


output/dates.ics: out.json post_process.py validator.py
	python post_process.py
#	python validator.py

website:

force:
	touch website
	make

out.json: website blueroom.py
	rm -f out.json
	scrapy runspider blueroom.py --out out.json


output/%.ics: output/%.json
	python post_process.py $<
	python validator.py $@

output/%.json:
	python process.py $(*F)

