from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
    flash,
)
from flask_login import current_user, login_required

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from .htcondor import checkuser, checkexperiment, load_jobjson
from .utilites import get_formatted_date
import sys

website_blueprint = Blueprint("website", __name__)


@website_blueprint.route("/")
def home():
    return render_template("EHTGatewayHome.html", user=current_user)


@website_blueprint.route("/about")
# @login_required
def about():
    return render_template("about.html", user=current_user)


@website_blueprint.route("/dashboard")
# @login_required
def dashboard():
    message = checkuser(current_user.nickname, simple=False)
    print(message, file=sys.stdout)
    # return render_template("dashboard.html", user=current_user,message=message)
    datestr = get_formatted_date()
    return render_template(
        "EHTGatewayDashboard.html", user=current_user, datestr=datestr, message=message
    )


@website_blueprint.route("/ipoleexplorer")
# @login_required
def ipoleexplorer():
    # return render_template("ipoleexplorer.html", user=current_user)
    datestr = get_formatted_date()
    return render_template("EHTIpoleExplorer.html", user=current_user, datestr=datestr)


@website_blueprint.route("/ipolebatch")
# @login_required
def ipolebatch():
    # return render_template("ipolebatch.html", user=current_user)
    datestr = get_formatted_date()
    return render_template("EHTIpoleBatch.html", datestr=datestr, user=current_user)


@website_blueprint.route("/experiments")
# @login_required
def experiments():
    message = checkuser(current_user.nickname)
    # return render_template("experiments.html", user=current_user,message = message)
    datestr = get_formatted_date()
    return render_template(
        "EHTExperiments.html", user=current_user, message=message, datestr=datestr
    )


@website_blueprint.route("/experiment/<experimentid>")
# @login_required
def experiment(experimentid):
    """show the status of the experiment with id"""

    message = checkexperiment(experimentid)

    if "error" in message:
        flash(message["error"])
        return redirect(url_for("website.experiments"))

    # return render_template("experiment.html", user=current_user, message = message)
    return render_template(
        "EHTGatewayJobStatus.html", user=current_user, message=message
    )


@website_blueprint.route("/experimenthistory/<experimentid>")
# @login_required
def experimenthistory(experimentid):
    """display the experiment summary page"""

    message = load_jobjson(experimentid)

    return render_template(
        "EHTGatewayJobSumarry.html", user=current_user, message=message
    )


@website_blueprint.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")

    if not query:
        return render_template("components/search_results.html", results=[])

    ix = open_dir("index")
    with ix.searcher() as searcher:
        query_parser = QueryParser("content", ix.schema)
        parsed_query = query_parser.parse(query)
        results = searcher.search(parsed_query)
        return render_template("components/search_results.html", results=results)


@website_blueprint.route("/jupyterlite/")
@website_blueprint.route("/jupyterlite/<path:path>")
# @login_required
def jupyterlite(path="index.html"):
    return send_from_directory("static/jupyter", path)


@website_blueprint.route("/plottingtool")
# @login_required
def plottingtool():
    # return render_template("experiments.html", user=current_user,message = message)
    images = {
        "bestbet_imgs4": "static/image/plot_images/bestbet_imgs4.png",
        "bestbet_corr": "static/image/plot_images/bestbet_corr.png",
        "bestbet_forward": "static/image/plot_images/bestbet_forward.png",
        "bestbet_liklyhood": "static/image/plot_images/bestbet_liklyhood",
        "bestbet_sedgrid": "static/image/plot_images/bestbet_sedgrid.png",
        "bestbet_snapshot": "static/image/plot_images/bestbet_snapshot.png",
        "bestbet_stat": "static/image/plot_images/bestbet_stat.png",
        "bestbet_va_sed": "static/image/plot_images/bestbet_va_sed.png",
    }
    return render_template("EHTPlotting.html", user=current_user, images=images)


@website_blueprint.route("/settings")
# @login_required
def settings():
    return render_template("EHTGatewaySettings.html", user=current_user)


@website_blueprint.route("/jupyterlab")
# @login_required
def jupyterlab():
    # run jupyterlab
    return redirect("http://eht.scigap.org:8888/lab", token="my-token")
