# cryptobot
 A simple trading bot using python.

## Environment

```shell
pip install -r requirements.txt
```

## Dependencies
You will need to obtain application credentials for 
[Coinbase Pro](https://docs.cloud.coinbase.com).
## Run

After following the setup instructions, run the program:

```shell
python3 main.py [-h] -t TICKER
```

## Arguments

    |short|long|default|help|
    | :---: | :---: | :---: | :---: |
    |`-h`|`--help`||show this help message and exit|
    |`-t`|`--ticker`|`BTC-USDC`|Cryptocurrency ticker symbol.|