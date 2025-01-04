test:
	coverage run --source=berlinonline.jinjardf -m pytest -vv -s berlinonline/jinjardf/tests && coverage html

temp/class_hierarchy.nt: berlinonline/jinjardf/tests/data/class_hierarchy.ttl temp
	rapper -i turtle -o ntriples $< > $@

temp/class_hierarchy.reduced.nt: temp/class_hierarchy.nt
	cat $< | grep -v "label" | grep -v "rdf-schema#Class" > $@

temp/class_hierarchy.dot: temp/class_hierarchy.reduced.nt
	rapper -i ntriples -o dot $< | \
		sed 's/rankdir = LR/rankdir = BT/g' | \
		sed 's|http://www.w3.org/2000/01/rdf-schema#|rdfs:|g' | \
		sed 's|https://berlinonline.github.io/jinja-rdf/example/class_hierarchy/|ex:|g' | \
		grep -v 'label="\\n\\nModel:\\n(Unknown)";' > $@

temp/class_hierarchy.png: temp/class_hierarchy.dot
	dot -Tpng -o$@ $<

temp:
	mkdir -p temp

example/output:
	mkdir -p example/output

clean: clean-temp clean-output

clean-temp:
	rm -rf temp

clean-output:
	rm -rf example/output
