import pandas as pd

def json_to_df(file):
    """
    Converts the 'data' value from json result to a pandas dataframe
    """
    d = [[j[key] for key in j.keys()] for j in file['data']]  # Put the 'data' value into a list of lists
    col_lst = list(file['data'][0].keys())  # Define the column name
    df = pd.DataFrame(data=d, columns=col_lst)  # change to dataframe
    return df