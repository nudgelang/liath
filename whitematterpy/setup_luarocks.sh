#!/bin/bash

# Install necessary system dependencies
sudo apt-get update
sudo apt-get install -y libssl-dev

# Install LuaRocks packages
luarocks install luasocket
luarocks install luasec
luarocks install lua-cjson
luarocks install lyaml
luarocks install html-entities
luarocks install markdown

echo "LuaRocks packages installed successfully!"