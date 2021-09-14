#!/bin/bash
set -e

pip install -r requirements.txt
python glossary.py
git checkout json
if diff glossary.json assets/glossary.json >/dev/null ; then
  echo "No changes to json"
else
  echo "json changed - updating repo"
  mv -v glossary.json assets
  git config --local user.email "action@github.com"
  git config --local user.name "GitHub Action"
  git add assets
  git commit -m "Update glossary.json"
  git push
fi
