import argparse
from ast import arg
from src.crawling_data import *
import os.path

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, help='Input dir for data')
    args = parser.parse_args()
    data_content = pd.DataFrame([])
    tickers = get_tickers()
    with PoolExecutor(max_workers=5) as executor:
        for _results in executor.map(ticker_information, tickers):
            data_content = pd.concat([data_content, _results], ignore_index=True)
    data_content['ticker'].replace('', np.nan, inplace=True)
    data_content.dropna(subset=['ticker'], inplace=True)
    if os.path.exists(args.data_path) == True:
        print(f"Exist file {args.data_path}\nUpdating file...")
        try:
            check_data(args.data_path,data_content)
        except:
            pass
        print("Done")
    else:
        print(f"Creating file {args.data_path}...")
        data_content.to_csv(args.data_path)
        print("Done")
