from StakePy.client import Client
from StakePy.models import Var, Currency
from StakePy.strategy import (
    DiceStrategy,
    Rule,
    Every,
    Increase,
    Reset
)


def main():
    every_1_wins               = Every(1, Var.WINS)
    every_1_losses             = Every(1, Var.LOSSES)
    reset_bet_amount           = Reset(Var.BET_AMOUNT)
    increase_bet_amount_by_15  = Increase(Var.BET_AMOUNT, 15)
    
    rules = [
        Rule(
            on=every_1_wins,
            do=reset_bet_amount
        ),
        Rule(
            on=every_1_losses,
            do=increase_bet_amount_by_15
        )
    ]

    client   = Client.from_dotenv()
    strategy = DiceStrategy(client, base_chance=9)
    strategy.run(rules)



if __name__ == '__main__':
    main()