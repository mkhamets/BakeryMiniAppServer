#!/bin/bash

# Build script for Bakery Mini App Server
# Generates timestamps for cache busting while preserving cart/user data

echo "🔧 Starting build process..."

# Generate timestamp for cache busting
TIMESTAMP=$(date +%s)
echo "📅 Generated timestamp: $TIMESTAMP"

# Update HTML files with timestamp
echo "📝 Updating HTML files with timestamp..."
sed -i '' "s/{{BUILD_TIMESTAMP}}/$TIMESTAMP/g" bot/web_app/index.html

# Update CSS files with timestamp (if needed)
echo "🎨 Updating CSS files with timestamp..."
sed -i '' "s/{{BUILD_TIMESTAMP}}/$TIMESTAMP/g" bot/web_app/style.css

# Update JavaScript files with timestamp (if needed)
echo "⚡ Updating JavaScript files with timestamp..."
sed -i '' "s/{{BUILD_TIMESTAMP}}/$TIMESTAMP/g" bot/web_app/script.js

echo "✅ Build process completed!"
echo "📊 Timestamp: $TIMESTAMP"
echo "🚀 Ready for deployment!"
