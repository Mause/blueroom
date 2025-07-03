all: output/blueroom.org.au.ics output/ourgoldenage.com.au.ics output/dates.ics output/index.html


website:

force:
	touch website
	make

out.json: website blueroom.py
	rm -f out.json
	scrapy runspider blueroom.py --out out.json

output/%.ics: output/%.json post_process.py
	python post_process.py $< $@
	docker run --rm -v $(pwd):/data faph/icalendar-validator /data/output/$@

output/%.json:
	python process.py $(*F)

output/index.html:
	python index.py
