pydoc_config = '{ renderer: { type: markdown, data_code_block: true, data_expression_maxlength: 500, render_toc: true, header_level_by_type: {"Method": 3, "Function": 3, "Variable": 3 } } }'

.PHONY: test
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

clean: clean-temp clean-output clean-doc

clean-temp:
	rm -rf temp

clean-output:
	rm -rf example/output

clean-doc:
	rm -rf doc

doc:
	mkdir -p doc

temp/rdf_environment.md: temp
	pydoc-markdown -I berlinonline -m jinjardf.rdf_environment ${pydoc_config} > $@

temp/rdf_filters.md: temp
	pydoc-markdown -I berlinonline -m jinjardf.rdf_filters ${pydoc_config} > $@

temp/site_generator.md: temp
	pydoc-markdown -I berlinonline -m jinjardf.site_generator ${pydoc_config} > $@

temp/theme.md: temp
	pydoc-markdown -I berlinonline -m jinjardf.theme ${pydoc_config} > $@

temp/%.with_links.md: temp/%.md
	python bin/markdown_links.py --input $< > $@

temp/%.no_toc_root.md: temp/%.with_links.md
	python bin/delete_toc_root.py --input $< > $@

doc/%.md: temp/%.no_toc_root.md doc
	python bin/raw_codeblocks.py --input $< > $@

documentation: doc/rdf_filters.md doc/rdf_environment.md doc/site_generator.md doc/theme.md
