#!/bin/sh

if [ ! -d ./tmp ] 
then
    mkdir -p ./tmp
fi

python ./benchmark/driver.py -did DPSZ9NG -w 1 -cw 0 -bw 1

pdflatex ./benchmark/tex_template.tex
rm tex_template.aux
rm tex_template.log
