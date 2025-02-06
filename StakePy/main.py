import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional

@dataclass
class BetInfo:
    target: int
    result: int
    side: str
    profit: int

    def is_win(self):
        return (
            self.result > self.target
            if self.side == 'high'
            else
            self.result < self.target
        )
    
class Session:
    def __init__(self, api_key):
        self._api_key = api_key
        
    def roll(self, bet_amount, win_chance_or_multiplier, side='high'):
        result = random.randint(0, 9999)
        target = win_chance_or_multiplier
        return BetInfo()

def every(n: int, condition: str) -> bool:
    def wrapper(strategy):
        match condition:
            case 'wins':
                

def increase(x: str, by_percentage: int):
    def wrapper(session):
        match x:
            case 'bet_amount':
                session.next_bet_amount = (
                    session.previous_bet_amount + 
                    session.previous_bet_amount *
                    by_percentage / 100
                )
            case 'win_chance':
                session.next_win_chance = (
                    session.previous_win_chance + 
                    session.previous_win_chance *
                    by_percentage / 100
                )

class Rule:
    def __init__(
        self,
        on=every(1, 'losses'),
        do=increase('bet_amount', 100)
    ) -> None:
        self._on = on
        self._do = do

    def apply(self, strategy):
        if self._on(strategy):
            return self._do

class Strategy:
    def __init__(self, session, base_bet_amount=1):
        self._session = session
        self._rules = []
        self.base_bet_amount = base_bet_amount
        self.next_bet_amount = 0
        self.previous_bet_amount = 0
        self.wins = 0
        self.losses = 0
        self.current_wins_streak = 0
        self.current_losses_streak = 0


    def add_rule(self, rule: Rule):
        self._rules.append(rule)
    
    def add_rules(self, *rules):
        self._rules.extend(rules)
        
    def run(self):
        while True:
            session.roll()

def main() -> None:
    '''
    strategy = Strategy(Session(1234))
    strategy.add_rule(
        Rule(
            on=every(1, 'losses'),
            do=increase('bet_amount', 100)
        )
    )
    strategy.run()
    '''
    for _ in range(10):
        bet_info = BetInfo(target=5000, result=random.randint(0, 9999), side='low', profit='123')
        print(bet_info)
        print(bet_info.is_win())
if __name__ == '__main__':
    main()