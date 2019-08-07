#!/bin/sh

if [ ! -d ./tmp ] 
then
    mkdir -p ./tmp
fi

python ./benchmark/driver.py -did DP10XVX -w 1 -cw 1 -bw 2

pdflatex ./benchmark/tex_template.tex
rm tex_template.aux
rm tex_template.log
