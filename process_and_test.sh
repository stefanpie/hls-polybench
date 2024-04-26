#!/usr/bin/env bash
python ./process.py -j 32 -s SMALL --output-suffix "__testing_small"
python ./test.py -j 32 -r