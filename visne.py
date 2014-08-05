#! /opt/local/bin/python
import flowml as fml

fd = fml.FlowData('test.fcs')

fd.tsne('visne', sample = 20000, verbose = True, backgate = True)

fd.fcs_export('test_export.fcs')


