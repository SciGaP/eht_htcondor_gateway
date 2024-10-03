from flask import Blueprint, render_template, request, send_from_directory
from flask_login import current_user, login_required

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from .htcondor import checkuser, checkexperiment

website_blueprint = Blueprint("website", __name__)

@website_blueprint.route("/")
def home():
    return render_template("EHTGatewayHome.html", user=current_user)

@website_blueprint.route("/about")
#@login_required
def about():
    return render_template("about.html", user=current_user)

@website_blueprint.route("/dashboard")
#@login_required
def dashboard():
    message = checkuser(current_user.nickname,simple=True)
    #return render_template("dashboard.html", user=current_user,message=message)
    return render_template("EHTGatewayDashboard.html", user=current_user,message=message)

@website_blueprint.route("/ipoleexplorer")
#@login_required
def ipoleexplorer():
    return render_template("ipoleexplorer.html", user=current_user)

@website_blueprint.route("/ipolebatch")
#@login_required
def ipolebatch():
    return render_template("ipolebatch.html", user=current_user)

@website_blueprint.route("/experiments")
#@login_required
def experiments():
    message = checkuser(current_user.nickname)
    return render_template("experiments.html", user=current_user,message = message)

@website_blueprint.route("/experiment/<experimentid>")
#@login_required
def experiment(experimentid):
    """show the status of the experiment with id"""

    message = checkexperiment(experimentid)

    return render_template("experiment.html", user=current_user, message = message)

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