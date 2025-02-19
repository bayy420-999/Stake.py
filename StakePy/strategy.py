import os
import time

from rich import print
from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.table import Table, Column
from rich.console import Console, Group

from typing import (
    Self,
    Optional
)

from .client import Client
from .models import (
    Var,
    Currency,
    DiceModifiers,
    BetInfo,
    DiceTargetCondition
)
from .errors import (
    InsufficientBalanceError,
    InsignificantBetError
)

class Every:
    def __init__(
        self: Self,
        n_times: int,
        var: Var
    ) -> None:
        self._n_times   = n_times
        self._count     = 0
        self.repr       = f'EVERY_{n_times}_{var.name}'

        match var:
            case Var.BETS:
                self._counter_fn = self._bets_counter
            case Var.WINS:
                self._counter_fn = self._wins_counter
            case Var.LOSSES:
                self._counter_fn = self._losses_counter
 
    def __call__(
        self: Self,
        bet_info: BetInfo
    ) -> bool:
        self._counter_fn(bet_info)

        if self._count == self._n_times:
            self._count = 0
            return True
        return False

    def _bets_counter(
        self: Self,
        bet_info: BetInfo
    ) -> None:
        self._count += 1

    def _wins_counter(
        self: Self,
        bet_info: BetInfo
    ) -> None:
        current_state = bet_info.win

        match current_state:
            case True:
                self._count += 1
            case False:
                pass

    def _losses_counter(
        self: Self,
        bet_info: BetInfo
    ) -> None:
        current_state = bet_info.win

        match current_state:
            case True:
                pass
            case False:
                self._count += 1

class EveryStreakOf:
    def __init__(
        self: Self,
        n_times: int,
        var: Var
    ) -> None:
        self._n_times        = n_times
        self._count          = 0
        self._previous_state = None
        self.repr            = f'EVERY_STREAK_OF_{n_times}_{var.name}'

        match var:
            case Var.BETS:
                self._counter_fn = self._bets_counter
            case Var.WINS:
                self._counter_fn = self._wins_counter
            case Var.LOSSES:
                self._counter_fn = self._losses_counter

    def __call__(
        self: Self,
        bet_info: BetInfo
    ) -> bool:
        self._counter_fn(bet_info)

        if self._count == self._n_times:
            self._count = 0
            return True
        return False

    def _bets_counter(
        self: Self,
        bet_info: BetInfo
    ) -> None:
        self._count += 1

    def _wins_counter(
        self: Self,
        bet_info: BetInfo
    ) -> None:
        previous_state       = False if self._previous_state is None else self._previous_state
        current_state        = bet_info.win
        self._previous_state = current_state
 
        match previous_state, current_state:
            case [True, True]   | [False, True]: self._count += 1
            case [False, False] | [True, False]: self._count  = 0

    def _losses_counter(
        self: Self,
        bet_info: BetInfo
    ) -> None:
        previous_state       = True if self._previous_state is None else self._previous_state
        current_state        = bet_info.win
        self._previous_state = current_state
 
        match previous_state, current_state:
            case [True, True]   | [False, True]: self._count  = 0
            case [False, False] | [True, False]: self._count += 1

class Increase:
    def __init__(
        self: Self,
        var: Var,
        by: int | float
    ) -> None:
        self._by  = by
        self.repr = f'INCREASE_{var.name}_BY_{by}'
        
        match var:
            case Var.CHANCE:
                self._increase_fn = self._increase_chance
            case Var.BET_AMOUNT:
                self._increase_fn = self._increase_bet_amount

    def __call__(
        self: Self,
        modifiers: DiceModifiers
    ) -> None:
        self._increase_fn(modifiers)

    def _increase_chance(
        self: Self,
        modifiers: DiceModifiers
    ) -> None:
        current_chance   = modifiers.chance
        next_chance      = current_chance + (current_chance * (self._by / 100))
        modifiers.chance = next_chance

    def _increase_bet_amount(
        self: Self,
        modifiers: DiceModifiers
    ) -> None:
        current_bet_amount   = modifiers.bet_amount
        next_bet_amount      = current_bet_amount + (current_bet_amount * (self._by / 100))
        modifiers.bet_amount = next_bet_amount

class Reset:
    def __init__(
        self: Self,
        var: Var
    ) -> None:
        self.var  = var
        self.repr = f'RESET_{var.name}'

    def __call__(
        self: Self,
        modifiers: DiceModifiers
    ) -> None:
        match self.var:
            case Var.CHANCE:
                modifiers.chance = modifiers.base_chance
            case Var.BET_AMOUNT:
                modifiers.bet_amount = modifiers.base_bet

class Rule:
    def __init__(self, on, do):
        self._on  = on
        self._do  = do
        self.repr = f'(on={on.repr}, do={do.repr})'

    def __call__(self, bet_info, modifiers):
        if self._on(bet_info):
            self._do(modifiers)

class Strategy:
    def __init__(self, client, modifiers=None, rules=None):
        self._client    = client
        self.rules     = [] if rules is None else rules
        self.modifiers = (
            modifiers
            if modifiers
            else
            DiceModifiers(
                base_bet=0.000011,
                bet_amount=0.000011,
                currency=Currency.USDT,
                base_chance=49.5,
                chance=49.5,
                dice_target_condition=DiceTargetCondition.ABOVE
            )
        )
        self.statistics = Statistics(
            balance=self.get_available_balance(),
            bets=0,
            wins=0,
            losses=0,
            profit=0,
            wagered=0
        )
        self.bet_table  = Table(
            Column('No'),
            Column('Bet Id'),
            Column('Payout Multiplier'),
            Column('Amount'),
            Column('Payout')
        )

    def generate_stats_panel(self):
        balance = Text(f'BALANCE  : {self.statistics.balance:.8f}\n')
        bets    = Text(f'BETS     : {self.statistics.bets}\n')
        wins    = Text('WINS     : ').append_text(
            Text(
                f'{self.statistics.wins}\n',
                style='green'
            )
        )
        losses  = Text('LOSSES   : ').append_text(
            Text(
                f'{self.statistics.losses}\n',
                style='red'
            )
        )
        profit  = Text('PROFIT   : ').append_text(
            Text(
                f'{self.statistics.profit:.8f}\n',
                style=(
                    'green'
                    if self.statistics.profit > 0
                    else
                    'red'
                )
            )
        )
        wagered = Text(f'WAGERED  : {self.statistics.wagered:.8f}\n')
        return Panel(
            Text()
            .append_text(balance)
            .append_text(bets)
            .append_text(wins)
            .append_text(losses)
            .append_text(profit)
            .append_text(wagered)
        )

    def get_available_balance(self):
        return [
            balance.available.amount
            for balance in self._client.get_user_balances()
            if balance.available.currency == self.modifiers.currency
        ][0]

    def run(self, rules=None):
        if rules:
            self.rules = rules

        with Live(
            Group(
                self.generate_stats_panel(),
                self.bet_table
            )
        ) as live:
            while True:
                bet_info = self._client.dice_roll(
                    amount=self.modifiers.bet_amount,
                    currency=self.modifiers.currency,
                    chance=self.modifiers.chance,
                    dice_target_condition=self.modifiers.dice_target_condition
                )

                for rule in self.rules:
                    rule(bet_info, self.modifiers)

                bet_id            = bet_info.id
                payout_multiplier = bet_info.payout_multiplier
                amount            = bet_info.amount
                payout            = bet_info.payout

                self.statistics.balance  = self.get_available_balance()
                self.statistics.profit  += payout - amount
                self.statistics.wagered += amount
                self.statistics.bets    += 1
                if bet_info.win:
                    self.bet_table.add_row(
                        Text(str(self.statistics.bets), style='green'),
                        Text(bet_id, style='green'),
                        Text(str(payout_multiplier), style='green'),
                        Text(f'{amount:.8f}', style='green'),
                        Text(f'{payout:.8f}', style='green'),
                    )
                    self.statistics.wins += 1
                else:
                    self.bet_table.add_row(
                        Text(str(self.statistics.bets), style='red'),
                        Text(bet_id, style='red'),
                        Text(str(payout_multiplier), style='red'),
                        Text(f'{amount:.8f}', style='red'),
                        Text(f'{payout:.8f}', style='red'),
                    )
                    self.statistics.losses += 1

                for column in self.bet_table.columns:
                    if len(column._cells) > 10:
                        column._cells.pop(0)

                live.update(
                    Group(
                        self.generate_stats_panel(),
                        self.bet_table
                    ),
                    refresh=True
                )