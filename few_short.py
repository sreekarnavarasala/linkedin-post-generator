import json
import pandas as pd

class FewShotPosts:
    def __init__(self, filepath="processed_posts.json"):
        self.df = None
        self.unique_tags = None
        self.load_posts(filepath)

    def load_posts(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            posts = json.load(f)
            self.df = pd.json_normalize(posts)
            
            # Correcting column naming and ensuring Length column creation
            self.df["Length"] = self.df["line_count"].apply(self.categorize_length)
            
            # Extract unique tags
            all_tags = self.df["tags"].apply(lambda x: x).sum()
            self.unique_tags = set(all_tags)

    def categorize_length(self, line_count):
        if line_count < 5:
            return "Short"
        elif 5 <= line_count <= 10:
            return "Medium"
        else:
            return "Long"

    def get_tags(self):
        return self.unique_tags

    def get_filtered_posts(self, length, language, tag):
        # Filter the DataFrame based on the given conditions
        df_filtered = self.df[
            (self.df["language"] == language) &
            (self.df["Length"] == length) &
            (self.df["tags"].apply(lambda tags: tag in tags))
        ]

        return df_filtered.to_dict(orient="records")

if __name__ == "__main__":
    # Initialize the FewShotPosts class and fetch filtered posts
    fs = FewShotPosts()
    posts = fs.get_filtered_posts("Short", "English", "Job Search")
    print(posts)
