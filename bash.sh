#!/bin/bash
i=0
while test  $i -le 4 
do
	echo Number: $i
	((i++))
done

echo -n "Enter a number: "
read VAR

if test $VAR -gt 10 
then
  echo "The variable is greater than 10."
fi
