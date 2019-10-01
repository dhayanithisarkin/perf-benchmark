#!/bin/sh

if [ ! -d ./tmp ]; then
  mkdir -p ./tmp
fi
cmd="python ./benchmark/driver.py"
if test -z "$1"; then
  read -p "Enter DID (Default[Home Depot] = DP10XVX) : " DID
  read -p "Enter Start of Current Time Frame [YYYY-MM-DD-HH] (Default yesterday's time): " cs
  read -p "Enter End of Current Time Frame [YYYY-MM-DD-HH] (Default current time): " ce
  read -p "Enter Start of Base Time Frame [YYYY-MM-DD-HH] (Default day before yesterday's time): " bs
  read -p "Enter End of Base Time Frame [YYYY-MM-DD-HH] (Default yesterday's time): " be

  if ! test -z "$DID"; then
    cmd="$cmd -did $DID"
  fi
  if ! test -z "$cs"; then
    cmd="$cmd -cs $cs"
  fi
  if ! test -z "$ce"; then
    cmd="$cmd -ce $ce"
  fi
  if ! test -z "$bs"; then
    cmd="$cmd -bs $bs"
  fi
  if ! test -z "$be"; then
    cmd="$cmd -be $be"
  fi
else
  cmd+=" $@"
fi

eval $cmd
#pdflatex -interaction=batchmode ./benchmark/tex_template.tex

#rm tex_template.aux
#rm tex_template.log
