# -*- coding: utf-8 -*-
import treetaggerwrapper

path = '/export/tools/tree-tagger/galician-par-linux-3.2.bin.gz'
tagger = treetaggerwrapper.TreeTagger(TAGLANG='gl', TAGDIR='/export/tools/tree-tagger/')

tags = tagger.tag_text(u"Imos necesitar algo máis ca café .")

for token in tags:
	print token.strip().split('\t')
