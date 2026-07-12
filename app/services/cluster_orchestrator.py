from app import db
import sqlalchemy as sa
from app.models.public_comment import PublicComment
from app.services.hearing_service import get_hearing_by_id
from app.services.comment_service import get_comment
from app.services.clustering_service import cluster_comments
from app.models.comment_cluster import CommentCluster
#gets the hearing then sends all comments from that hearing to 
#cluster_comments() - but only sends the body and id
def run_clustering(hearing_id):
    try:
        hearing = get_hearing_by_id(hearing_id)
        if hearing is None:
            raise ValueError(f"hearing {hearing_id} not found")
        #gets all the comments form that hearing
        comments = get_comment(hearing_id)
        #gos throgh each comment from the hering and  turns them to a dict
        #with just there id and body
        comments_dict=[{"id":c.id, "body":c.body} for c in comments]
        #sends the body and id to the function that callst the api 
        clusters_data=cluster_comments(comments_dict)
        #to actually run it
        db.session.execute(
            sa.update(PublicComment) # "I want to update the PublicComment table"
            .where(PublicComment.hearing_id == hearing_id) # "only rows matching this condition"
            .values(cluster_id=None) # "set this column to this value, on all matching rows"
        )
        db.session.execute(
            sa.delete(CommentCluster)
            .where(CommentCluster.hearing_id == hearing_id)
        ) 
        #creates a dict of all the commetnts ids from the hearing 
        #so that i can use it to look up it up when im checking which comment
        #is connect it to the cluster
        comment_index = {c.id: c for c in comments}
        #goes trough each cluster in clusters data
        saved_clusters = []
        for cluster_data in clusters_data:
            #makes a new row for each cluster 
            cluster = CommentCluster(hearing_id=hearing_id, name=cluster_data["name"], description=cluster_data["description"])
            db.session.add(cluster)
            #the reason for flush is becasue i need the id that gets created
            #when instering to the db. i need it so that i can link the comments
            #to the cluster.flush makes u do that without having to insert everything
            db.session.flush()
            saved_clusters.append(cluster)
            #loops through each comment id in the cluster data and sets the cluster id 
            #for that comment to the id of the cluster that was just created
            for cid in cluster_data["comment_ids"]:
                comment_index[cid].cluster_id = cluster.id
        db.session.commit()
        return saved_clusters
    except Exception:
        db.session.rollback()
        raise

def get_cluster(hearing_id):
    cluster = CommentCluster.query.filter_by(hearing_id=hearing_id).all()
    return cluster