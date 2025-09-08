#!/bin/bash

input=$1
outro="/Volumes/LaCie/Google Drive/Data/Travel & Tourism/Marketing & Web 
Dev/Videos/Tiktok/outro/BT-animated-logo.mp4"
output="${input%.*}_outro.mp4"

ffmpeg -i "$input" -i "$outro" -filter_complex 
"[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" 
"$output"


