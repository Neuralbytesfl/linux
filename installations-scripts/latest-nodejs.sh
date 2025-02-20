#!/bin/bash

# Exit immediately if any command fails
set -e

echo "Fetching the latest Node.js version..."
NODE_VERSION=$(curl -s https://nodejs.org/dist/latest/ | grep -o 'v[0-9]*\.[0-9]*\.[0-9]*' | head -1)
NODE_DIST="node-${NODE_VERSION}-linux-x64"

echo "Downloading Node.js ${NODE_VERSION}..."
wget -q "https://nodejs.org/dist/latest/${NODE_DIST}.tar.xz" -O "/tmp/${NODE_DIST}.tar.xz"

echo "Extracting Node.js..."
tar -xf "/tmp/${NODE_DIST}.tar.xz" -C /tmp

echo "Moving Node.js to /usr/local/nodejs..."
sudo rm -rf /usr/local/nodejs
sudo mv "/tmp/${NODE_DIST}" /usr/local/nodejs

echo "Setting up environment variables for the current user..."

# Add Node.js to the current user's ~/.profile for permanent access
if ! grep -q 'export PATH=/usr/local/nodejs/bin:$PATH' ~/.profile; then
    echo 'export PATH=/usr/local/nodejs/bin:$PATH' >> ~/.profile
fi

# Apply the changes immediately for the current session
export PATH=/usr/local/nodejs/bin:$PATH

echo "Cleaning up..."
rm "/tmp/${NODE_DIST}.tar.xz"

echo "Verifying installation..."
node -v
npm -v

echo "Node.js ${NODE_VERSION} installation completed successfully! Please restart your terminal or run 'source ~/.profile' to apply changes."
