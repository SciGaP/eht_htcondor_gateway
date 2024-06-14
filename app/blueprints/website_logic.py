from flask import Blueprint, render_template, request, send_from_directory
from flask_login import current_user, login_required

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

website_blueprint = Blueprint("website", __name__)

@website_blueprint.route("/")
def home():
    return render_template("home.html", user=current_user)

@website_blueprint.route("/about")
#@login_required
def about():
    return render_template("about.html", user=current_user)

@website_blueprint.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    if not query:
        return render_template('components/search_results.html', results=[])

    ix = open_dir('index')
    with ix.searcher() as searcher:
        query_parser = QueryParser('content', ix.schema)
        parsed_query = query_parser.parse(query)
        results = searcher.search(parsed_query)
        return render_template('components/search_results.html', results=results)