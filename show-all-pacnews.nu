#!/usr/bin/env nu

def main [] {
    fd --unrestricted .*\.pacnew / | lines
}
