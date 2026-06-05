from flask import Flask, render_template, request, jsonify
from models import db
from services import KeywordService, PhotoService

app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)


@app.route("/", methods=["GET", "POST"])
def home():
    """Render the gallery. POST searches by keyword; GET shows the latest photos."""
    photos = []
    keyword_input = ""
    if request.method == "POST":
        keyword_input = request.form.get("keyword", "")
        photos = PhotoService.search_by_keyword(keyword_input)
    else:
        photos = PhotoService.get_all_photos()
    return render_template("index.html", photos=photos, keyword_input=keyword_input)


@app.route("/suggest_keywords")
def suggest_keywords():
    """Return keyword suggestions as JSON for the debounced autocomplete UI."""
    q = request.args.get("q", "")
    return jsonify(KeywordService.suggest(q))


if __name__ == "__main__":
    app.run(debug=True)
