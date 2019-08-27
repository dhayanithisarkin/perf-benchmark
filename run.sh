#!/bin/sh

if [ ! -d ./tmp ]; then
  mkdir -p ./tmp
fi
cmd="python ./benchmark/driver.py"

read -p "Enter DID (Default[Home Depot] = DP10XVX) : " DID
if ! test -z "$DID"; then
  cmd="$cmd -did $DID"
fi
read -p "Enter Window (Default 1 day): " w
if ! test -z "$w"; then
  cmd="$cmd -w $w"
fi
read -p "Enter Current Time (Default 0): " cw
if ! test -z "$cw"; then
  cmd="$cmd -cw $cw"
fi
read -p "Enter Base Time (Default 1): " bw
if ! test -z "$bw"; then
  cmd="$cmd -bw $bw"
fi

eval $cmd
pdflatex ./benchmark/tex_template.tex

rm tex_template.aux
rm tex_template.log
