pip install -r requirements.txt
python glossary.py
git checkout json
if diff glossary.json assets/glossary.json >/dev/null ; then
  mv -v glossary.json assets
  git config --local user.email "action@github.com"
  git config --local user.name "GitHub Action"
  git add assets
  git commit -m "Update glossary.json"
  git push
else
  echo "No changes to json"
fi
