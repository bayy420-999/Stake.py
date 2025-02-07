
from enum import StrEnum, auto
from dataclasses import dataclass

QUERIES = {}
QUERIES['user_balances'] = '''
query UserBalances {
    user {
        id
        balances {
            available {
                amount
                currency
                __typename
            }
            vault {
                amount
                currency
                __typename
            }
            __typename
        }
        __typename
    }
}
'''

QUERIES['dice_roll'] = '''
mutation DiceRoll(
    $amount: Float!,
    $target: Float!,
    $condition: CasinoGameDiceConditionEnum!,
    $currency: CurrencyEnum!,
    $identifier: String!
) {
    diceRoll(
        amount: $amount
        target: $target
        condition: $condition
        currency: $currency
        identifier: $identifier
    ) {
        ...CasinoBet
        state {
            ...CasinoGameDice
        }
    }
}

fragment CasinoBet on CasinoBet {
    id
    active
    payoutMultiplier
    amountMultiplier
    amount
    payout
    updatedAt
    currency
    game
    user {
        id
        name
    }
}

fragment CasinoGameDice on CasinoGameDice {
    result
    target
    condition
}
'''

class Var(StrEnum):
    BETS       = auto()
    WINS       = auto()
    LOSSES     = auto()
    BET_AMOUNT = auto()
    CHANCE     = auto()

class Currency(StrEnum):
    BTC  = auto()
    ETH  = auto()
    LTC  = auto()
    TRX  = auto()
    USDT = auto()
    USDC = auto()

class TargetCondition(StrEnum):
    ABOVE = auto()
    BELOW = auto()

class Game(StrEnum):
    DICE  = auto()
    LIMBO = auto()

@dataclass
class User:
    id  : str
    name: str

@dataclass
class DiceState:
    target          : float
    result          : float
    target_condition: TargetCondition

@dataclass
class DiceRoll:
    id               : str
    active           : bool
    payout_multiplier: int
    amount_multiplier: int
    amount           : float
    payout           : float
    updated_at       : str
    currency         : Currency
    game             : Game
    user             : User
    state            : DiceState

@dataclass
class BetInfo:
    data: DiceRoll

@dataclass
class Statistics:
    ...

@dataclass
class Modifiers:
    base_bet: float
    bet_amount: float
    base_chance: float
    chance: float
    target_condition: TargetCondition

    
    