import json 
import os
from groq import Groq
from dotenv import load_dotenv
from app.models.hearing_summary import Hearingsummary
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a civic-affairs analyst. Given a legislative hearing, return a JSON object with exactly these four keys:
- issue_description: a concise 1-3 sentence description of the central issue being addressed
- stakeholders: a comma-separated list of key individuals, groups, or organizations involved
- key_arguments: a summary of the main arguments presented (2-4 sentences)
- community_impact: how this hearing outcome may affect the broader community (1-3 sentences)
Return ONLY valid JSON. No markdown, no explanation, no extra text."""
#takes the hearing as input 
# The -> dict is a type hint, just telling you what it returns — in this case a dictionary 
#with the 4 fields. It doesn't enforce anything, it's just documentation.
def summarize_hearing(hearing) -> dict:
    #creates a list with two strings already in it, the title and date pulled from the 
    #hearing object. These always get included no matter what.
    parts = [f"Title: {hearing.title}", f"Date: {hearing.date}"]
    #checks if the hearing has a transcript at all. If it's None or empty, skip it.
    if hearing.transcript:
    #adds the transcript to the list, but only the first 15000 characters so the 
    #prompt doesn't overflow the AI's context window.
        parts.append(f"Transcript:\n{hearing.transcript[:15000]}")
    #checks if the hearing has a agends at all. If it's None or empty, skip it.    
    if hearing.agenda:
        # adds the agenda to the list
        parts.append(f"Agenda:\n{hearing.agenda}")
    #takes all those list items and joins them into one big string with a blank line 
    #between each section. That becomes the actual message you send to Groq.
    user_content = "\n\n".join(parts)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    #gets the response from the ai and removes any leading/trailing whitespace.
    raw = response.choices[0].message.content.strip()
    # left with just the raw JSON string that you can actually parse. Otherwise
    #json.loads() would fail.
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        #turns raw into a json 
        result = json.loads(raw)
        #meaning Groq returned something that isn't valid JSON at all.
    except json.JSONDecodeError as exc:
        raise ValueError(f"summarize_hearing: unparseable response: {raw!r}") from exc

    required =  {"issue_description", "stakeholders", "key_arguments", "community_impact"}
    missing = required - result.keys()
    #check after it is what catches the case where the JSON parsed fine but one of the 4 
    #required fields isn't in it.
    if missing:
     raise ValueError(f"summarize_hearing: response missing keys {missing}: {raw!r}")
    #is a dict comprehension that picks only those 4 keys out of the parsed JSON.
    return {k: result[k] for k in required}
    #this function is used to extract the gov decision from the transcript
def extract_decision(hearing) -> str:
    parts = [f"title:{hearing.title}",f"date:{hearing.date}"]
     
    if hearing.transcript:
        parts.append(f"Transcript:\n{hearing.transcript[:15000]}")
    hearing_sum= Hearingsummary.query.filter_by(hearing_id=hearing.id).first()
    if hearing_sum:
        parts.append(f"Issue: {hearing_sum.issue_description}")
        parts.append(f"Key Arguments: {hearing_sum.key_arguments}")
        parts.append(f"Community Impact: {hearing_sum.community_impact}")
    user_content = "\n\n".join(parts)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"system",
                "content": """You are a civic-affairs analyst. Based on the hearing title, date, and any available summary, write exactly 2 sentences describing what the government likely decided or what the outcome of this hearing was.
                No markdown, no JSON, no extra text."""
            },
            {"role":"user", "content":user_content}
        ],
         )
    return response.choices[0].message.content.strip()