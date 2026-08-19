import json 
import os
from groq import Groq

#pulls the model name from .env, falls back to the same model used for summarization
CLUSTERING_MODEL = os.environ.get("CLUSTERING_MODEL", "openai/gpt-oss-120b")
#created once at the top of the file, not inside the function, so we're not 
#reconnecting to Groq every single time cluster_comments() runs
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#tells the ai exactly what job to do, what input to expect (id + body pairs),
#and what shape to return the answer in (a JSON array of cluster objects)
SYSTEM_PROMPT = """ You are a civic-affairs analyst. Given a list of public comments (each with an id and body), group them into thematic clusters.

Return ONLY a valid JSON array. Each element must have exactly these keys:
- name: a short theme label (e.g. "Affordability", "Traffic Safety")
- description: a 1-2 sentence summary of what comments in this cluster share
- comment_ids: an array of integer IDs belonging to this cluster

Rules:
- Every comment ID from the input must appear in exactly one cluster.
- Do not invent IDs or omit any.
- Return ONLY the JSON array. No markdown, no explanation, no extra text """


#pure function - no db calls in here, just ai logic
#comments is expected to be a list of {"id": ..., "body": ...} dicts,
#already slimmed down by cluster_orchestrator.py before it gets here
def cluster_comments(comments):
    #guard clause - clustering is meaningless with 0 or 1 comments,
    #nothing to compare against yet, so stop immediately
    if len(comments) < 2:
        raise ValueError("cluster_comments: need at least 2 comments to cluster")

    #that takes your list of {"id": ..., "body": ...} dicts and turns it into one 
    #JSON-formatted string you can hand to the AI as "content"
    user_content = json.dumps(comments)

    response = client.chat.completions.create(
        model = CLUSTERING_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    #gets the raw text back from the ai and removes leading/trailing whitespace
    raw = response.choices[0].message.content.strip()
    #strips markdown code fences if the ai wrapped its answer in ```json ... ```
    #otherwise json.loads() below would fail on the backticks
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        #turns the raw string into an actual python list/dict structure
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        #ai returned something that isn't valid json at all
        raise ValueError(f"cluster comments: unparseable response: {raw!r}") from exc

    #the full set of every comment id that came IN to this function -
    #this is the "ground truth" we'll check the ai's output against
    input_ids = {c["id"] for c in comments}
    #starts empty, gets filled in as we walk through the ai's clusters below -
    #tracks every id we've seen so far across all clusters
    assigned_ids = set()

    #walk through each cluster the ai returned
    for cluster in result:
        #make sure the cluster actually has all 3 required fields -
        #catches a malformed/incomplete cluster object early
        for key in ("name", "description", "comment_ids"):
            if key not in cluster:
                raise ValueError(f"cluster_comments: cluster missing key '{key}': {cluster!r}")
        #walk through this cluster's own list of comment ids
        for cid in cluster["comment_ids"]:
            #if we've already seen this id in an earlier cluster, that's a
            #contradiction - a comment can't belong to two clusters at once
            if cid in assigned_ids:
                raise ValueError(f"cluster_comments: comment id {cid} appears in multiple clusters")
            #first time seeing this id - record it
            assigned_ids.add(cid)

    #only AFTER walking through every cluster can we know for sure whether
    #any input id never got assigned anywhere - can't check this mid-loop
    missing = input_ids - assigned_ids
    if missing:
        raise ValueError(f"cluster_comments: input IDs missing from output: {missing}")

    #validation passed - safe to hand back to cluster_orchestrator.py
    return result