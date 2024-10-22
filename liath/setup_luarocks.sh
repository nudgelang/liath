#!/bin/bash

# Install necessary system dependencies
sudo apt-get update
sudo apt-get install -y libssl-dev

# Install LuaRocks packages
luarocks install luasocket --tree .
luarocks install luasec --tree .
luarocks install lua-cjson --tree .
luarocks install lyaml --tree .
luarocks install html-entities --tree .
luarocks install markdown --tree .

echo "LuaRocks packages installed successfully!"