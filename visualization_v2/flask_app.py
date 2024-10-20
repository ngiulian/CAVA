from flask import Flask

from data_preprocessing import preprocess_dfs
from build_map import create_map

app = Flask(__name__)


@app.route("/")
def fullscreen():
    """Simple example of a fullscreen map."""
    chat_questions_df, completion_questions_df = preprocess_dfs()
    m = create_map(
        dfs = [completion_questions_df, chat_questions_df],
        df_names = ['completion', 'chat'],
        question_types=set(chat_questions_df['type'])
    )
    return m.get_root().render()

if __name__ == "__main__":
    app.run(debug=True)