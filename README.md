# StakePy - Stake.com API Wrapper

StakePy is Stake.com API Wrapper built on Python.

## Installation

```console
$ git clone https://github.com/bayy420-999/StakePy.git
$ cd StakePy
```

## Usage

Run the program by running `main.py` with the command below.

```console
$ python main.py
```

## `main.py` file explained

The default `main.py` file will run Stake.com Dice-Bot with following settings.

```
BASE_BET=0.00001
CURRENCY=USDT
BASE_CHANCE=49.5
TARGET_CONDITION=ABOVE
ON_EVERY_1_LOSSES=INCREASE_BET_AMOUNT_BY_100
ON_EVERY_1_WINS=RESET_BET_AMOUNT
```

To change the behaviour of the bot, you need to modify `main.py` file.

Here is the breakdown of `main.py` file, and how the bot works. Hopefully you can modify the file yourself after reading the explaination :).

### Importing needed class/function from StakePy

```python3
# Importing Client.
# This Client object is basically your Stake.com "account".
from StakePy.client import Client

# Importing Var, Currency, and TargetCondition.
# Var: 
#   Short for Variable is Enum class that contain constants
#   such as BETS, WINS, LOSSES and so on
#   that will be used to determine bot behaviour.
# Currency: 
#   Enum class that contain constants of supported currencies on Stake.com
#   such as BTC, ETH, LTC, USDT, and so on.
# TargetCondition:
#   Enum class that contain constants of dice target condition
#   that will be used to determine dice roll target condition (BELOW/ABOVE).
from StakePy.models import (
    Var,
    Currency,
    TargetCondition
)

# Importing DiceStrategy, Rule, Every, Increase, Reset.
# DiceStrategy:
#   The class that responsible to make dice bet, or basically the bot.
# Rule:
#   The class that responsible to determine the action to be performed if certain condtion meets.
# Every:
#   TODO: Write explaination
# Increase:
#   TODO: Write explaination
# Reset:
#   TODO: Write explaination
from StakePy.strategy import (
    DiceStrategy,
    Rule,
    Every,
    Increase,
    Reset
)
```

### Initialize Client

- Initialize `Client` by passing argument to `Client` constructor

```python3
# Remember kids, write everything inside main()
# and use if __name__ == '__main__' as entry point 
# to run main() hehe.
def main():
    API_KEY       = YOUR_STAKE_API_KEY
    CF_CLEARANCE  = YOUR_STAKE_CF_CLEARANCE
    CF_BM         = YOUR_STAKE_CF_BM
    CFUVID        = YOUR_STAKE_CFUVID

    client = Client(
        API_KEY,
        CF_CLEARANCE,
        CF_BM,
        CFUVID
    )
```