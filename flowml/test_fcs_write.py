#! /opt/local/bin/python
import fcs

data, metadata, analysis, meta_analysis = fcs.read('test.fcs')

fcs.write('test_write.fcs',data, metadata)

