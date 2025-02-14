
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

QUERIES['limbo_bet'] = '''
mutation LimboBet(
    $amount: Float!,
    $multiplierTarget: Float!,
    $currency: CurrencyEnum!,
    $identifier: String!
) {
    limboBet(
        amount: $amount
        currency: $currency
        multiplierTarget: $multiplierTarget
        identifier: $identifier
    ) {
        ...CasinoBet
        state {
        ...CasinoGameLimbo
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

fragment CasinoGameLimbo on CasinoGameLimbo {
    result
    multiplierTarget
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

class DiceTargetCondition(StrEnum):
    ABOVE = auto()
    BELOW = auto()

class Game(StrEnum):
    DICE  = auto()
    LIMBO = auto()

@dataclass
class Available:
    amount: float
    currency: Currency

@dataclass
class Vault:
    amount: float
    currency: Currency


@dataclass
class Balance:
    available: Available
    vault    : Vault

@dataclass
class User:
    id  : str
    name: str

@dataclass
class DiceState:
    target          : float
    result          : float
    dice_target_condition: DiceTargetCondition

@dataclass
class LimboState:
    result           : float
    multiplier_target: float

@dataclass
class BetInfo:
    id               : str
    active           : bool
    payout_multiplier: int
    amount_multiplier: int
    payout           : float
    amount           : float
    updated_at       : str
    currency         : Currency
    game             : Game
    user             : User
    state            : DiceState | LimboState

@dataclass
class Statistics:
    ...

@dataclass
class Modifiers:
    base_bet: float
    bet_amount: float
    base_chance: float
    chance: float
    dice_target_condition: DiceTargetCondition

    
    