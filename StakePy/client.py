from __future__ import annotations

import os
import time
import requests
from rich import print
from dotenv import load_dotenv
from typing import Self, Optional
#from strategy import Every
from .errors import InsufficientBalanceError, InsignificantBetError
from .models import (
    Game,
    User,
    Currency,
    DiceRoll,
    DiceState,
    BetInfo,
    TargetCondition,
    QUERIES
)


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
        enum_type: Game | Currency | Condition,
        key: str
    ) -> Game | Currency | Condition:
        try:
            return enum_type.__members__[key.upper()]
        except KeyError:
            raise
 
    def _construct_response(
        self: Self,
        json_response: dict[str, str]
    ) -> BetInfo:
        match json_response:
            case {
                'errors': [
                    {
                        'errorType': error_type,
                        'message': message
                    },
                    *errors
                ]
            }:
                if error_type == 'insufficientBalance':
                    raise InsufficientBalanceError(message)
                if error_type == 'insignificantBet':
                    raise InsignificantBetError(message)
            case {'data': {'diceRoll': data}}:
                bet_id = data['id']
                active = data['active']
                payout_multiplier = data['payoutMultiplier']
                amount_multiplier = data['amountMultiplier']
                amount = data['amount']
                payout = data['payout']
                updated_at = data['updatedAt']
                currency = self._get_enum(Currency, data['currency'])
                game = self._get_enum(Game, data['game'])
                user = User(
                    id=data['user']['id'],
                    name=data['user']['name']
                )
                state = DiceState(
                    target=data['state']['target'],
                    result=data['state']['result'],
                    target_condition=self._get_enum(TargetCondition, data['state']['condition'])
                )
                data = DiceRoll(
                    id=bet_id,
                    active=active,
                    payout_multiplier=payout_multiplier,
                    amount_multiplier=amount_multiplier,
                    amount=amount,
                    payout=payout,
                    updated_at=updated_at,
                    currency=currency,
                    game=game,
                    user=user,
                    state=state
                )

                return BetInfo(
                    data=data
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
        try:
            json_data = dict(
                query=QUERIES['user_balances'],
                operationName='UserBalances'
            )
            return self._session.post(self.STAKE_API_URL, json=json_data).json()
        except Exception:
            raise

    def dice_roll(
        self: Self,
        amount: float,
        currency: Currency,
        chance: float,
        target_condition: Condition,
        identifier: Optional[str]='PeLCm-dvHjrDsj-CeIKCk'
    ) -> BetInfo:
        try:
            json_data = dict(
                query=QUERIES['dice_roll'],
                variables=dict(
                    amount=amount,
                    currency=currency.value,
                    target=chance if target_condition == TargetCondition.BELOW else 100 - chance,
                    condition=target_condition.value,
                    identifier=identifier
                )
            )
            json_response = self._session.post(self.STAKE_API_URL, json=json_data).json()
            #print(json_response)
            return self._construct_response(json_response)
        except Exception:
            #print(json_response)
            raise
    
def main():
    client = Client.from_dotenv()
if __name__ == '__main__':
    main()



