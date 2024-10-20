import pandas as pd
from googletrans import Translator

class LanguageTranslator:
    def __init__(self, dest, src="en"):
        self.dest = dest
        self.src = src
        self.translator = Translator()

    def translate_column(self, df, col_name, batch_size=500):
        translated_texts = []
        for i in range(0, len(df), batch_size):
            batch = df[col_name].iloc[i:i+batch_size].to_list()
            attempts = 0
            success = False
            while attempts < 3 and not success:
                try:
                    translations = self.translator.translate(batch, src=self.src, dest=self.dest)
                    translated_texts.extend([translation.text for translation in translations])
                    success = True
                except Exception as e:
                    attempts += 1
                    print(f"Error during translation, attempt {attempts}: {e}")
            if not success:
                # Fallback: append the original text if translation fails
                translated_texts.extend(batch)

            print(f"Finished batch {i}-{i+batch_size}")

        df[col_name] = translated_texts

if __name__ == "__main__":
    LT = LanguageTranslator('zh-cn')
    df = pd.read_csv('data/questions/chat_questions.csv')
    column_names = ['prompt_classification', 'prompt_open_ended_version_0', 'prompt_open_ended_version_1', 'prompt_open_ended_version_2']
    for col_name in column_names:
        LT.translate_column(df, col_name)
        print(f"Translated column: {col_name}")
    output_csv = 'data/questions/chinese_chat_questions.csv'
    df.to_csv(output_csv, index=False)

