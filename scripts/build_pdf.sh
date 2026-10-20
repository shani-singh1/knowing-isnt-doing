#!/bin/bash
# Compile paper.tex with Tectonic and report undefined references, overfull boxes and the page count.
# Usage: TECTONIC=/path/to/tectonic scripts/build_pdf.sh
set -u
cd "$(dirname "$0")/.."
"${TECTONIC:-tectonic}" --keep-logs paper.tex > /dev/null 2>&1
echo "undefined or duplicate references:"
grep -i -E "undefined|multiply defined" paper.log | head -5
echo "overfull boxes: $(grep -c Overfull paper.log)"
grep -A2 Overfull paper.log | head -8
grep -o "Output written.*" paper.log
rm -f paper.log paper.aux paper.out
