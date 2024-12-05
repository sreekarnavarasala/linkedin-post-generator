import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm

def get_unified_tags(enriched_posts):
    unique_tags = set()
    for post in enriched_posts:
        unique_tags.update(post['tags'])
    unique_tags_list = ', '.join(unique_tags)

    template = ''' I will give you a list of tags. You need to unify tags with the following requirements:
    1. Tags are unified and merged to create a shorter list.
       Example-1: "Job Seekers", "Job Hunting" can all be merged into a single tag "Job Search"
       Example-2: "Motivation", "Inspiration", "Drive" can be mapped to "Motivation"
       Example-3: "Personal Growth", "Personal Development", "Self Improvement" can be mapped to "Self Improvement"
       Example-4: "Scam Alert", "Job Scam" etc. can be mapped to "Scams"
    2. Each tag should follow title case convention. Example: "Motivation", "Job Search"
    3. Output should be a JSON object, no preamble
    4. Output should have a mapping of the original tag and the unified tag.
       For example: {{"Job Seekers": "Job Search", "Job Hunting": "Job Search", "Motivation": "Motivation"}}

    Here is the list of tags:
    {tags}
    '''
    
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'tags': str(unique_tags_list)})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Content too big. Unable to parse tags.")
    
    return res

def extract_metadata(post):
    template = ''' 
    You are given a LinkedIn post. You need to extract the number of lines, language of the post, and tags.
    1. Return a valid JSON. No Preamble
    2. JSON object should have exactly three keys: line_count, language, and tags.
    3. Tags should be an array of text tags. Extract a minimum of two tags.
    4. Language should be English.

    Here is the actual post on which you need to perform this task:
    {post}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={'post': post})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context is too big. Unable to parse the post.")
    
    return res

def process_posts(raw_file_path, processed_file_path="processed_posts.json"):
    enriched_posts = []
    with open(raw_file_path, 'r', encoding='utf-8') as file:
        posts = json.load(file)
        for post in posts:
            metadata = extract_metadata(post['text'])
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags = get_unified_tags(enriched_posts)

    for post in enriched_posts:
        current_tags = post['tags']
        new_tags = {unified_tags[tag] for tag in current_tags if tag in unified_tags}
        post['tags'] = list(new_tags)

    with open(processed_file_path, mode="w", encoding='utf-8') as outfile:
        json.dump(enriched_posts, outfile, indent=4)

if __name__ == "__main__":
    process_posts("raw_posts.json", "processed_posts.json")
