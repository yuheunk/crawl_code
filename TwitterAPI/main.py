# Library
from TweetAPI import TweetSettings, CrawlTweet
from dataset import json_to_df
import json

def main():
    twitter = TweetSettings()
    # If there is a separate file with additonal parameters for query,load the file.
    # setting_dir = None
    setting_dir = './twitter_settings.txt'

    if setting_dir:  # If a file path is given load the file
        params = twitter.load_settings(setting_dir)
    else:  # Otherwise let the user input the parameters manually
        params = twitter.settings(max_results='a', recency=False)
    
    crawler = CrawlTweet()
    q = input("Input query to search for: ")  # Get the query as input
    crawler.search(query=q, settings=params)  # Search using the input query and parameters
    
    json_result = crawler.result  # save the json format result to a new variable
    with open('twitter_result.json', 'w') as output_file:  # save result to json file
        json.dump(json_result, output_file, indent=3)
    
    df_result = json_to_df(json_result)  # convert the json file to dataframe for only the data values
    df_result.to_csv('twitter_result.csv', index=False)  # save csv file

if __name__ == "__main__":
    main()