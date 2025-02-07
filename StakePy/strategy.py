import os
import time
from rich import print
from typing import (
    Self,
    Optional,
    Generic,
    TypeVar
)

from .client import Client
from .models import (
    Var,
    Currency,
    Modifiers,
    BetInfo,
    TargetCondition
)


T = TypeVar('T')
class Condition(Generic[T]):
    ...

class Action(Generic[T]):
    ...
class Every:
    def __init__(
        self: Self,
        n_times: Optional[int]=1,
        var: Optional[Var]=Var.LOSSES
    ) -> None:
        self.n_times = n_times
        self.var = var
        self.predicate = f'`every {self.n_times} {self.var.value}`'
        self._internal_counter = 0

    def __repr__(self):
        return f'<Every object <predicate={self.predicate}> at {hex(id(self))}>'

    def __call__(self, bet_info):
        print(bet_info)
        match self.var:
            case Var.BETS:
                self._internal_counter += 1
            case Var.WINS:
                if bet_info.data.payout_multiplier > 0:
                    self._internal_counter += 1
                else:
                    self._internal_counter = 0
            case Var.LOSSES:
                if bet_info.data.payout_multiplier == 0:
                    self._internal_counter += 1
                else:
                    self._internal_counter = 0

        if self._internal_counter == self.n_times:
            self._internal_counter = 0
            return True
        return False

class Reset:
    def __init__(
        self: Self,
        var: Var=Var.BET_AMOUNT
    ) -> None:
        self.var = var

    def __call__(self, modifiers: Modifiers):
        match self.var:
            case Var.BET_AMOUNT:
                modifiers.bet_amount = modifiers.base_bet
            case Var.CHANCE:
                modifiers.chance = modifiers.base_chance

class Increase:
    def __init__(
        self: Self,
        var: Var=Var.BET_AMOUNT,
        by: int | float=100
    ) -> None:
        self.var = var
        self.by = by

    def __call__(self, modifiers: Modifiers):
        match self.var:
            case Var.BET_AMOUNT:
                modifiers.bet_amount += modifiers.bet_amount * self.by / 100
            case Var.CHANCE:
                modifiers.chance += modifiers.chance * self.by / 100
            case _: raise ValueError()

class Rule:
    def __init__(
        self: Self,
        on: Condition[Every],
        do: Action[Increase | Reset]
    ) -> None:
        self.on = on
        self.do = do

    def __call__(
        self: Self,
        bet_info: BetInfo,
        modifiers: Modifiers
    ):
        if self.on(bet_info):
            self.do(modifiers)

class DiceStrategy:
    def __init__(
        self: Self,
        client: Client,
        base_bet: Optional[int | float]=0.00001,
        base_chance: Optional[float]=49.5,
        currency: Optional[Currency]=Currency.USDT,
        target_condition: Optional[TargetCondition]=TargetCondition.ABOVE
    ) -> None:
        self._client = client
        self.modifiers = Modifiers(
            base_bet=base_bet,
            bet_amount=base_bet,
            base_chance=base_chance,
            chance=base_chance,
            target_condition=target_condition
        )
        self.currency = currency
        self.rules = None

    def run(self: Self, rules: Optional[list[Rule] | None]=None) -> None:
        self.rules = rules
        while True:
            try:
                bet_info = self._client.dice_roll(
                    amount=self.modifiers.bet_amount,
                    currency=self.currency,
                    chance=self.modifiers.chance,
                    target_condition=self.modifiers.target_condition
                )

                if rules:
                    for rule in rules:
                        rule(bet_info, self.modifiers)

                print(bet_info)
                #os.system('clear')
                #time.sleep(0.1)
            except Exception:
                raise
