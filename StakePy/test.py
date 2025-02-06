import time
from random import randint
from enum import Enum, auto
from typing import Callable
from decimal import Decimal, Context, ROUND_DOWN
from dataclasses import dataclass, field

class Side(Enum):
    HIGH = auto()
    LOW  = auto()

class Var(Enum):
    BETS       = auto()
    WINS       = auto()
    LOSSES    = auto()
    BET_AMOUNT = auto()
    CHANCE     = auto()

@dataclass
class BetInfo:
    bet_id    : int
    bet_amount: Decimal
    chance    : Decimal
    target    : Decimal
    result    : Decimal
    side      : Side
    won       : bool 
    multiplier: Decimal
    profit    : Decimal

CONTEXT_PREC_4 = Context(prec=4)
CONTEXT_PREC_8 = Context(prec=8)

class Client:
    def __init__(self, api_key, balance=1):
        self._bet_id  = 0
        self._api_key = api_key
        self._balance = balance

    def get_balance(self):
        return self._balance

    def roll(self, bet_amount, chance, side=Side.HIGH):
        bet_amount     = CONTEXT_PREC_8.create_decimal(bet_amount)
        chance         = CONTEXT_PREC_4.create_decimal(chance)
        target         = CONTEXT_PREC_4.create_decimal(Decimal(1) + chance)
        result         = CONTEXT_PREC_4.create_decimal(randint(0, 10000) / 100)
        won            = result > target if side == Side.HIGH else result < target
        multiplier     = CONTEXT_PREC_4.create_decimal(
            (mult     := Decimal(100) / chance) -
            (mult      * Decimal(0.01))
        )
        multiplier     = multiplier if won else -multiplier
        profit         = CONTEXT_PREC_8.create_decimal(bet_amount * multiplier)
        self._bet_id  += 1
        self._balance += profit

        return BetInfo(
            bet_id=self._bet_id,
            bet_amount=bet_amount,
            chance=chance,
            target=target,
            result=result,
            side=side,
            won=won,
            multiplier=multiplier,
            profit=profit
        )

def every(n_times: int=1, var: Var=Var.LOSSES) -> Callable:
    def _every(
        current_session: CurrentSession
    ) -> bool:
        match var:
            case Var.BETS:
                if current_session.running_bets == n_times:
                    current_session.running_bets = 0
                    return True
                return False
            case Var.WINS:
                if current_session.running_wins == n_times:
                    current_session.running_wins = 0
                    return True
                return False
            case Var.LOSSSES:
                if current_session.running_losses == n_times:
                    current_session.running_losses = 0
                    return True
                return False
            case _: raise ValueError()
    return _every

def every_streak_of(n_times: int=1, var: Var=Var.LOSSES) -> Callable:
    def _every_streak_of(
        current_session: CurrentSession
    ) -> bool:
        match var:
            case Var.BETS:
                if current_session.running_bets == n_times:
                    current_session.running_bets = 0
                    return True
                return False
            case Var.WINS:
                if current_session.running_wins == n_times:
                    current_session.running_wins = 0
                    return True
                return False
            case Var.LOSSSES:
                if current_session.running_losses == n_times:
                    current_session.running_losses = 0
                    return True
                return False
            case _: raise ValueError()
    return _every


def increase(var: Var=Var.BET_AMOUNT, by: Decimal=CONTEXT_PREC_4.create_decimal(100)) -> Callable:
    def _increase(strategy: Strategy) -> None:
        match var:
            case Var.CHANCE:
                strategy.chance   = strategy.chance + strategy.chance * by / Decimal(100)
            case Var.BET_AMOUNT:
                strategy.prev_bet = strategy.next_bet
                strategy.next_bet = strategy.prev_bet + strategy.prev_bet * by / Decimal(100)
            case _: raise ValueError()
    return _increase

def reset(var: Var=Var.BET_AMOUNT) -> Callable:
    def _reset(strategy: Strategy) -> None:
        match var:
            case Var.CHANCE:
                strategy.chance = strategy.base_chance
            case Var.BET_AMOUNT:
                strategy.next_bet = strategy.base_bet
            case _: raise ValueError()
    return _reset

class Rule:
    def __init__(self, on=None, do=None):
        self._on = on
        self._do = do

    def __call__(self, strategy):
        if self._on(strategy.current_session):
            self._do(strategy)

@dataclass
class CurrentSession:
    bets                 : int = 0
    wins                 : int = 0
    losses               : int = 0
    running_wins         : int = 0
    running_losses       : int = 0
    current_wins_streak  : int = 0
    current_losses_streak: int = 0
    highest_wins_streak  : int = 0
    highest_losses_streak: int = 0

    biggest_bet_amount   : int = 0

class Strategy:
    def __init__(self, client, base_bet=0.00001, chance=49.5):
        self._client         = client
        self.base_bet        = CONTEXT_PREC_8.create_decimal(base_bet)
        self.prev_bet        = CONTEXT_PREC_8.create_decimal(0)
        self.next_bet        = self.base_bet
        self.chance          = CONTEXT_PREC_4.create_decimal(chance)
        self.base_chance     = self.chance
        self.current_session = CurrentSession()

    def run(self, *rules):
        while self._client.get_balance() > self.next_bet:
            bet_info = self._client.roll(self.next_bet, self.base_chance)
            if bet_info.won:
                self.current_session.wins                  += 1
                self.current_session.running_wins          += 1
                self.current_session.current_wins_streak   += 1
                self.current_session.current_losses_streak  = 0
            else:
                self.current_session.losses         += 1
                self.current_session.running_losses += 1
                self.current_session.current_wins_streak    = 0
                self.current_session.current_losses_streak += 1
            self.current_session.bets += 1
 
            for rule in rules:
                rule(self)
            
            profit = f'{profit}' if (profit := bet_info.profit).is_signed() else f' {profit}'
            print(f'{self.next_bet:>4} | {profit} | {self._client.get_balance()}')
            time.sleep(0.05)


class Every:
    def __init__(self, n_times: int=1, var: Var=Var.LOSSES):
        self.n_times          = n_times
        self.var              = var
        self.internal_counter = 0

    def __call__(self, bet_info: BetInfo):
        match self.var:
            case Var.BETS:
                self.internal_counter += 1
            case Var.WINS if bet_info.won is True:
                self.internal_counter += 1
            case Var.LOSSES if bet_info.won is not True:
                self.internal_counter += 1

        if self.internal_counter == self.n_times:
            self.internal_counter = 0
            return True
        return False

class EveryStreakOf:
    def __init__(self, n_times: int=1, var: Var=Var.LOSSES):
        self.n_times          = n_times
        self.var              = var
        self.prev_bet_info    = None
        self.internal_counter = 0

    def __call__(self, bet_info: BetInfo):
        match self.var:
            case Var.BETS:
                self.internal_counter += 1
            case Var.WINS:
                if (
                    bet_info.won is True and (
                        self.prev_bet_info is None
                        or self.prev_bet_info is True
                    )
                ):
                    self.internal_counter += 1
                else:
                    self.internal_counter = 0


        if self.internal_counter == self.n_times:
            self.internal_counter = 0
            return True
        return False


def main():
    '''
    every_1_wins               = every(1, Var.WINS)
    every_1_lossses            = every(1, Var.LOSSSES)
    reset_to_base_bet          = reset(Var.BET_AMOUNT)
    increase_bet_amount_by_100 = increase(Var.BET_AMOUNT, by=CONTEXT_PREC_4.create_decimal(200))

    strategy = Strategy(Client('API_KEY_001', 100), base_bet=1)
    strategy.run(
        Rule(
            on=every_1_lossses,
            do=increase_bet_amount_by_100
        ),
        Rule(
            on=every_1_wins,
            do=reset_to_base_bet
        )
    )
    '''
    every_streak_of_3_bets = EveryStreakOf(3, Var.BETS)
    every_streak_of_2_wins = EveryStreakOf(2, Var.WINS)
    client = Client(api_key='API_KEY_001')
    bet_infos = [client.roll(1, 49.5) for _ in range(10)]
    for bet_info in bet_infos:
        print(f'WON={int(bet_info.won)} | ESO3B={int(every_streak_of_3_bets(bet_info))} | ESO2W={int(every_streak_of_2_wins(bet_info))}')

if __name__ == '__main__':
    main()