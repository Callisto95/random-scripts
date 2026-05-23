#!/usr/bin/env nu

print "IPv4"
print (http get https://ipinfo.io/ip)
curl -4 https://icanhazip.com

print "IPv6"
print (http get https://api64.ipify.org)
curl -6 https://icanhazip.com
