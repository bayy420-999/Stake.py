from __future__ import annotations

import os
import time
import requests
from tenacity import (
    retry,
    wait_exponential,
    retry_if_exception_type,
    stop_after_attempt
)
from requests.exceptions import ConnectionError, JSONDecodeError
from rich import print
from dotenv import load_dotenv
from typing import Self, Optional, Callable
from .errors import InsufficientBalanceError, InsignificantBetError
from .models import (
    Game,
    User,
    Currency,
    DiceState,
    LimboState,
    BetInfo,
    DiceTargetCondition,
    QUERIES,
    Balance,
    Available,
    Vault
)

retry_predicates = (
    retry_if_exception_type(ConnectionError) |
    retry_if_exception_type(JSONDecodeError)
)

def print_attempt(retry_state):
    print('[red][bold]Error occured during function call.[/red][/bold]')
    print(f'Sleep for {int(retry_state.upcoming_sleep)} secs')
    print(f'Retrying for the {retry_state.attempt_number} attempts')

API_ERROR_TYPES = {
    'insufficientBalance': InsufficientBalanceError,
    'insignificantBet': InsignificantBetError
}

class Client:
    STAKE_API_URL = 'https://stake.krd/_api/graphql'

    def __init__(
        self: Self,
        api_key: str,
        cf_clearance: str,
        cf_bm: str,
        cfuvid: str
    ) -> None:
        self._session = requests.Session()
        self._headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
            'cookie': f'cf_clearance={cf_clearance}; __cf_bm={cf_bm}; _cfuvid={cfuvid}',
            'x-access-token': api_key
        }
        self._session.headers.update(self._headers)

    def _get_enum(
        self: Self,
        enum_type: Game | Currency | DiceTargetCondition,
        key: str
    ) -> Game | Currency | DiceTargetCondition:
        try:
            return enum_type.__members__[key.upper()]
        except KeyError:
            raise
 
    def _disable_ssl_verification(self):
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self._session.verify = False
        print('Warning: InsecureRequestWarning disabled.')

    @retry(
        retry=retry_predicates,
        wait=wait_exponential(multiplier=1, min=1, max=16),
        stop=stop_after_attempt(10),
        before_sleep=print_attempt
    )
    def _get_json_response(
        self: Self,
        json_data: dict[str, str]
    ) -> dict[str, str]:
        response = self._session.post(self.STAKE_API_URL, json=json_data)
        return response.json()

    def _get_data(self, json_response) -> dict[str, str]:
        match json_response:
            case {'errors': [
                    {
                        'errorType': error_type,
                        'message': message
                    },
                    *errors
                ]
            }:
                raise API_ERROR_TYPES[error_type](message)
            case {'data': {'user': {'balances': balances}}}:
                return list(map(self._construct_balance, balances))
            case {'data': data}:
                return self._construct_bet_info(data)
            case _: raise Exception('What u do bro?!?!?!')

    def _construct_balance(self, balance):
        match balance:
            case {
                'available': {
                    'amount': available_amount,
                    'currency': available_currency
                },
                'vault': {
                    'amount': vault_amount,
                    'currency': vault_currency
                }
            }:
                return Balance(
                    available=Available(
                        amount=available_amount,
                        currency=available_currency
                    ),
                    vault=Vault(
                        amount=vault_amount,
                        currency=vault_currency
                    )
                )

    def _construct_bet_info(
        self: Self,
        data: dict[str, str]
    ) -> BetInfo:
        game, bet_info = data.popitem()
 
        match game:
            case 'limboBet':
                state = LimboState(
                    result=bet_info['state']['result'],
                    multiplier_target=bet_info['state']['multiplierTarget']
                )
            case 'diceRoll':
                state = DiceState(
                    target=bet_info['state']['target'],
                    result=bet_info['state']['result'],
                    dice_target_condition=bet_info['state']['condition']
                )

        return BetInfo(
            id=bet_info['id'],
            active=bet_info['active'],
            payout_multiplier=bet_info['payoutMultiplier'],
            amount_multiplier=bet_info['amountMultiplier'],
            payout=bet_info['payout'],
            amount=bet_info['amount'],
            updated_at=bet_info['updatedAt'],
            currency=self._get_enum(Currency, bet_info['currency']),
            game=self._get_enum(Game, bet_info['game']),
            user=User(
                id=bet_info['user']['id'],
                name=bet_info['user']['name']
            ),
            state=state
        )

    @staticmethod
    def from_dotenv() -> Client:
        load_dotenv()
        match os.environ:
            case {
                'STAKE_API_KEY': API_KEY,
                'STAKE_CF_CLEARANCE': CF_CLEARANCE,
                'STAKE_CF_BM': CF_BM,
                'STAKE_CFUVID': CFUVID
            }:
                return Client(API_KEY, CF_CLEARANCE, CF_BM, CFUVID)
            case _: raise KeyError()

    def get_user_balances(self: Self) -> dict[str, str]:
        json_data = dict(
            query=QUERIES['user_balances'],
            operationName='UserBalances'
        )
        
        json_response = self._get_json_response(json_data)
        return self._get_data(json_response)


    def dice_roll(
        self: Self,
        amount: Optional[float]=0.00001,
        currency: Optional[Currency]=Currency.USDT,
        chance: Optional[float]=49.5,
        dice_target_condition: Optional[DiceTargetCondition]=DiceTargetCondition.ABOVE,
        identifier: Optional[str]='PeLCm-dvHjrDsj-CeIKCk'
    ) -> BetInfo:
        json_data = dict(
            query=QUERIES['dice_roll'],
            variables=dict(
                amount=amount,
                currency=currency.value,
                target=chance if dice_target_condition == DiceTargetCondition.BELOW else 100 - chance,
                condition=dice_target_condition.value,
                identifier=identifier
            )
        )

        json_response = self._get_json_response(json_data)
        return self._get_data(json_response)

    def limbo_bet(
        self: Self,
        amount: Optional[float]=0.00001,
        currency: Optional[Currency]=Currency.USDT,
        multiplier_target: Optional[float]=2.0,
        identifier: Optional[str]='PeLCm-dvHjrDsj-CeIKCk'
    ) -> BetInfo:
        json_data = dict(
            query=QUERIES['limbo_bet'],
            variables=dict(
                amount=amount,
                currency=currency.value,
                multiplierTarget=multiplier_target,
                identifier=identifier
            )
        )

        json_response = self._get_json_response(json_data)
        return self._get_data(json_response)
