from flask import Flask, render_template, request, jsonify
from models import db, Keyword, Photo
from services import PhotoService

app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    photos = []
    keyword_input = ""
    if request.method == "POST":
        keyword_input = request.form.get("keyword", "")
        photos = PhotoService.search_by_keyword(keyword_input)
    else:
        photos = PhotoService.get_all_photos()
    return render_template("index.html", photos=photos, keyword_input=keyword_input)

# New route for AJAX suggestions
@app.route("/suggest_keywords")
def suggest_keywords():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])

    # Search keywords containing the input
    matches = Keyword.query.filter(Keyword.keyword.ilike(f"%{q}%")).limit(10).all()
    result = [k.keyword for k in matches]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)