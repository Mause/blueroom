all: output/blueroom.org.au.ics output/ourgoldenage.com.au.ics output/queerscreen.org.au.ics output/index.html

clean:
	rm -rf output/*

website:

force:
	touch website
	make

out.json: website blueroom.py
	rm -f out.json
	scrapy runspider blueroom.py --out out.json

output/%.ics: output/%.json post_process.py
	python post_process.py $< $@
	docker run --rm -v $(shell pwd):/data faph/icalendar-validator /data/$@

output/%.json: process.py
	python process.py $(*F)

output/index.html: website index.py
	python index.py
