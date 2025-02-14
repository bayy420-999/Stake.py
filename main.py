#from rich import print
import json
from StakePy.client import Client
from StakePy.models import (
    Var,
    Currency,
    DiceTargetCondition
)
from StakePy.strategy import (
    DiceStrategy,
    Rule,
    Every,
    Increase,
    Reset,
    SwitchDiceTargetCondition
)


def main():
    every_1_wins                     = Every(1, Var.WINS)
    every_2_wins                     = Every(2, Var.WINS)
    every_1_losses                   = Every(1, Var.LOSSES)
    reset_bet_amount                 = Reset(Var.BET_AMOUNT)
    switch_dice_target_condition     = SwitchDiceTargetCondition()
    increase_bet_amount_by_3         = Increase(Var.BET_AMOUNT, 3)
    increase_bet_amount_by_15        = Increase(Var.BET_AMOUNT, 15)
    
    rules = [
        Rule(
            on=every_1_wins,
            do=reset_bet_amount
        ),
        Rule(
            on=every_2_wins,
            do=switch_dice_target_condition
        ),
        Rule(
            on=every_1_losses,
            do=increase_bet_amount_by_3
        )
    ]

    client   = Client.from_dotenv()
    #client._disable_ssl_verification()
    #for _ in range(100):
    
    print(client.limbo_bet())
    #print(client.get_user_balances())
    '''
    strategy = DiceStrategy(
        client,
        base_bet=0.0000101,
        base_chance=1,
        dice_target_condition=DiceTargetCondition.ABOVE
    )
    strategy.run(rules)
    '''


if __name__ == '__main__':
    main()