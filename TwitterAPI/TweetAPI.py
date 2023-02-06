import requests

class CrawlTweet:
    """
    This Class crawls the tweet based on 
    the given input query and additional query settings.
    """
    def __init__(self):
        self.token = input("Input your twitter account bearer token: ")
        self.headers = {"Authorization": "Bearer {}".format(self.token)}
    
    def set_url(self, query, settings):
        """
        Sets the url for the twitter API.
        """
        url = "https://api.twitter.com/2/tweets/search/recent?"
        addon = f"query={query}"
        for k, v in settings.items():
            if v is None:
                continue
            addon+=f'&{k}={v}'  # add in the parameters if their value is not None
        url+=addon
        return url  # final url for search
    
    def search(self, query, settings):
        self.url = self.set_url(query, settings)
        response = requests.request("GET", self.url, headers=self.headers)  # request the API output
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        self.result = response.json()  # save the json file into result
        

class TweetSettings:
    """
    This Class is to set up parameters that specify the query. 
    Four parameters from the Twitter developers documentation on API v2 are set up.
    - max_results
    - sort_order
    - tweet.fields
    - user.fields

    As they are optional parameters, the initial values will be set as None.
    """
    def __init__(self):
        self.max_results = None
        self.sort_order = None
        self.tweet_fields = None
        self.user_fields = None

    def set_max_result(self, max_results=None):
        while max_results:  # If a value is given for max_results
            try:
                # Test if the given input is an integer
                max_results = int(max_results)
                if max_results < 10:  # Those smaller than 10 should be fixed to 10
                    max_results = 10
                elif max_results > 100:  # Those bigger than 100 should be fixed to 100
                    max_results = 100
            except (TypeError,ValueError): 
                # Filter out TypeError(when an integer is not given)
                print("ERROR: Only integers are accepted for max_results. Try again")
                max_results = input('Input desired number of results between 10 and 100')
                continue  # continue until a correct form of input is given
            else: break  # break out of the while loop once an integer is given
        return max_results
    
    def set_order(self, recency=None):
        order = ['relevancy', 'recency']  # Define the two types of input for parameter 'sort_order'
        if recency is not None:  # when a boolean value is given
            sort_order = order[recency]
        else: sort_order = None
        return sort_order
    
    def set_fields(self, fields=None):
        if fields:  # if a list of fields are given
            fields = ",".join(fields)  # join the elements with comma as Twitter documentation specifies for both 'twitter.fields' and 'user.fields'
        return fields

    def settings(self, max_results=None, recency=None, tweet_fields=None, user_fields=None):
        """
        The following parameters specify the query but this is optional.
        (Documentation link: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)

        - max_results(int): maximum number of results to return (between 10 and 100)
        - recency(bool): True to return recent tweets, False will return relevant tweets
        - tweet_fields(list): This specifies Tweet fields that will be delivered in each returned Tweet object
        - user_fields(list): This specifies user fields that will be delivered in each returned Tweet object
        """
        
        self.max_results = self.set_max_result(max_results)
        self.sort_order = self.set_order(recency)
        self.tweet_fields = self.set_fields(tweet_fields)
        self.user_fields = self.set_fields(user_fields)
        print("-"*5+"Setting complete"+"-"*5)

        result = {
            'max_results': self.max_results,
            'sort_order': self.sort_order,
            'tweet.fields': self.tweet_fields,
            'user.fields': self.user_fields
            }
        # return a dictionary of the additional parameters for search
        return result

    def load_settings(self, file_path):
        """
        This function loads a txt file of the parameters.
        The file will one or multiple lines of the parameter name and their values
        split by '/' and written in each line as the following example.

        e.g.
        <Parameter name1>/<Parameter value1>
        <Parameter name2>/<Parameter value2>
        ...

        """
        f = open(file_path, 'r')
        result = {line.split('/')[0]:line.split('/')[1] for line in f}  # First create a dictionary from the raw file

        for k, v in result.items():
            v = v.strip('\n')  # Strip '\n' if there are any in the values
            result[k] = v
            if k=='max_results':  # For parameter 'max_results' the value should change into an integer
                result[k] = int(v)
            else: continue

        # For further application when a parameter is not specified,
        # it will be added to the result dictionary with the value 'None'
        key_lst = ['max_results', 'sort_order', 'tweet.fields', 'user.fields']
        for key in key_lst:
            result.setdefault(key)

        return result