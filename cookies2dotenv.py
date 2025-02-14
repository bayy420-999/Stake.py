import re
import argparse

def grab_cookies(file_handler):
    txt = file_handler.read()
    STAKE_API_KEY = re.search('\"x-access-token\": \"(.*?)\"', txt)[1]
    STAKE_CF_CLEARANCE = re.search('cf_clearance=(.*?);', txt)[1]
    STAKE_CF_BM = re.search('__cf_bm=(.*?);', txt)[1]
    STAKE_CFUVID = re.search('_cfuvid=(.*?);', txt)[1]
    print(f'STAKE_API_KEY={STAKE_API_KEY}\nSTAKE_CF_CLEARANCE={STAKE_CF_CLEARANCE}\nSTAKE_CF_BM={STAKE_CF_BM}\nSTAKE_CFUVID={STAKE_CFUVID}')

def main():
    parser = argparse.ArgumentParser(
        prog='cookies2dotenv',
        description='Grab required cookies to run `StakePy Bot` from cookies.txt file'
    )
    
    parser.add_argument('filename')
    args = parser.parse_args()
    filename = args.filename

    with open(filename, 'r') as file_handler:
        grab_cookies(file_handler)

if __name__ == '__main__':
    main()