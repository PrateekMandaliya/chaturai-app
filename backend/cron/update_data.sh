#!/bin/bash
echo "⏳ Updating articles and embeddings..."
cd /app/backend
python get_data.py
python embedding.py
echo "✅ Update complete."