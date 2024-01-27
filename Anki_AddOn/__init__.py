from aqt import mw
from aqt.reviewer import Reviewer
from anki.hooks import wrap, addHook
import json

# Load scores into config file:
def load_scores() -> dict:
    scores = {str : dict}
    scores = mw.col.get_config("scores", default = {})
    return scores

def update_score(reviewer, ease):
    scores = load_scores()
    deck_id = str(reviewer.card.did)

    # Initialize score and high score for the deck if not present
    if deck_id not in scores:
        scores[deck_id] = {"score": 0, "highscore": 0}

    # Increase score or reset to zero
    if ease > 1:  # 1 is 'again', 2-4 are 'hard', 'good', 'easy'
        scores[deck_id]["score"] += 1
    else:
        scores[deck_id]["score"] = 0

    # Update high score if necessary
    if scores[deck_id]["score"] > scores[deck_id]["highscore"]:
        scores[deck_id]["highscore"] = scores[deck_id]["score"]

    #load updated scores to config file
    scores = mw.col.set_config("scores", scores)
    mw.col.save()

    # Inject the updated score into the card's web view
    inject_score(reviewer, deck_id)

def inject_score(reviewer, deck_id):
    scores = load_scores()
    score = scores[deck_id]["score"] if deck_id in scores else 0
    highscore = scores[deck_id]["highscore"] if deck_id in scores else 0
    # Prepare the score HTML, but don't include the surrounding <div> here
    score_html = f"Score: {score} | High Score: {highscore}"

    # JavaScript to update or inject the score HTML
    inject_script = f"""
    (function() {{
        // Check if the 'anki-score' div already exists
        var scoreDiv = document.getElementById('anki-score');
        if (scoreDiv) {{
            // If it exists, just update its content
            scoreDiv.innerHTML = {json.dumps(score_html)};
        }} else {{
            // If it doesn't exist, create it and set its properties
            scoreDiv = document.createElement('div');
            scoreDiv.id = 'anki-score';
            scoreDiv.style.textAlign = 'center';
            scoreDiv.style.position = 'absolute';
            scoreDiv.style.bottom = '0';
            scoreDiv.style.width = '98%';
            scoreDiv.innerHTML = {json.dumps(score_html)};
            // Append the new 'anki-score' div to the '.card' element
            document.querySelector('.card').appendChild(scoreDiv);
        }}
    }})();
    """
    reviewer.web.eval(inject_script)

def on_profile_loaded():
    # Set all scores to 0
    scores = {str, dict}
    scores = mw.col.get_config("scores", default = 0)
    for deck_id in scores:
        scores[deck_id]["score"] = 0
    scores = mw.col.set_config("scores", scores)

    Reviewer._answerCard = wrap(Reviewer._answerCard, update_score, "after")

addHook("profileLoaded", on_profile_loaded)


