#returns JSON, used when the frontend makes a fetch call like 
#fetch('/api/hearings/1/summarize').
#i need a blue print so that my server dosent crash when 
#app.register_blueprint(api_bp, url_prefix="/api")
# blue print is like a mini  app that groups routes toghther 
#A Blueprint actually holds the routes
from flask import Blueprint
from flask import jsonify
from flask import request
from datetime import date
from app.services.hearing_service import list_hearings
from app.services.hearing_service import create_hearing
from app.services.hearing_service import get_hearing_by_id
from app.services.comment_service import create_comment
from app.services.comment_service import get_comment
from app.services.summary_orchestrator import run_summary
from app.services.cluster_orchestrator import run_clustering
from app.models.comment_cluster import CommentCluster
from app.services.government_decision_service import create_or_update_decision
from app.services.government_decision_service import get_decision

#"api" is the name flask uses to identify this blueprint
#name tells flask ehere the blue print lives so it can resolve the
#paths
api_bp = Blueprint("api", __name__)

@api_bp.route("/hearings", methods=["GET"])
def get_hearings():
    hearings = list_hearings()
    #jsonify converts python to json
    #but first it calls todict to convert the python to a dic
    #It loops through every hearing and converts it to a dictionary
    #so jsonify can turn it into JSON.
    return jsonify([h.to_dict() for h in hearings])

@api_bp.route("/hearings",methods=["POST"])
def create_hearings():
    data = request.get_json()
    title = data.get("title")
    raw_date = data.get("date")
    if title == None or raw_date == None:
        return jsonify({
            "error":"title and date are required"
        }),400
    parsed_date  = date.fromisoformat(raw_date)
    transcript = data.get("transcript")
    agenda = data.get("agenda")
    youtube_video_id  = data.get("youtube_video_id")
    hearing = create_hearing(title,parsed_date,transcript,agenda,youtube_video_id )
    return jsonify(hearing.to_dict()),201

@api_bp.route('/hearings/<int:id>',methods=["GET"])
def get_hearings_by_id(id):
    hearing = get_hearing_by_id(id)
    if hearing== None:
        return jsonify({
            "error":"Cant find hearing"
        }),404
    return jsonify(hearing.to_dict()),200

@api_bp.route('/hearings/<int:hearing_id>/comment',methods=["POST"])
def post_comment(hearing_id):
    data = request.get_json()
    body = data.get("body")
    if body == None:
        return jsonify({
            "error":"hearing id and comment are required"
        }),400
    comment = create_comment(body=body,hearing_id=hearing_id)
    return jsonify(comment.to_dict()),201
    
@api_bp.route('/hearings/<int:hearing_id>/comments',methods=["GET"])
def get_comments(hearing_id):
    comments = get_comment(hearing_id)
    return jsonify([c.to_dict() for c in comments])

@api_bp.route('/hearings/<int:hearing_id>/summarize',methods=["POST"])
def post_hearing(hearing_id):
    try:
        summ = run_summary(hearing_id)
    except ValueError:
        return jsonify({"error": "Hearing not found"}), 404
    return jsonify(summ.to_dict()), 200
#. It's what gets called when the "Cluster Comments" button gets clicked on the frontend 
@api_bp.route('/hearings/<int:hearing_id>/cluster', methods=["POST"])
def post_cluster(hearing_id):
    try:
        clusters = run_clustering(hearing_id)
    except ValueError as e:
        if str(e) == f"hearing {hearing_id} not found":
            return jsonify({"error": "Hearing not found"}), 404
        else:
            return jsonify({"error": "need at least 2 comments to cluster"}), 400
    return jsonify([c.to_dict() for c in clusters]), 200

#gets all the clusters for a hearing. It's what gets called when the
# front end loads the hearing page and needs to display the clusters for that hearing
@api_bp.route('/hearings/<int:hearing_id>/clusters', methods=["GET"])
def get_clusters(hearing_id):
    hearing = get_hearing_by_id(hearing_id)
    if hearing is None:
        return jsonify({"error": "Hearing not found"}), 404
    clusters = CommentCluster.query.filter_by(hearing_id=hearing_id).all()
    return jsonify([c.to_dict() for c in clusters]), 200

@api_bp.route('/hearings/<int:hearing_id>/decision', methods=["POST"])
def post_decision(hearing_id):
    data = request.get_json()
    decision_text = data.get("decision_text")
    raw_date = data.get("decision_date")
    if raw_date is not None:
        parsed_date = date.fromisoformat(raw_date)
    else:
        parsed_date = None  
    if decision_text is None:
        return jsonify({"error": "decision_text is required"}), 400
    try:  
        decision = create_or_update_decision(hearing_id, decision_text, parsed_date)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(decision.to_dict()), 201

@api_bp.route('/hearings/<int:hearing_id>/decision', methods=["GET"])
def get_decisions(hearing_id):
    decision = get_decision(hearing_id)
    if decision is None:
        return jsonify({"error": "Decision not found"}), 404
    return jsonify(decision.to_dict()), 200