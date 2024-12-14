"""
    Copyright 2024- ZiJian Jiang @ https://github.com/CallmeNezha

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from pony.orm import Database, Required, Optional, Set, PrimaryKey, db_session
import datetime
from collections import defaultdict
import pathlib


class FFDB:

    db_session = db_session
    db = None

    @staticmethod
    def bindDatabase(filename: pathlib.Path):

        if FFDB.db:
            FFDB.db.disconnect()
        #
        db = Database()


        class Meta(db.Entity):
            id = PrimaryKey(int, auto=True)
            version = Required(str)
            standard = Required(str)
            company = Required(str)
            month_from = Required(datetime.date)
            month_until = Required(datetime.date)

        class Currency(db.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str, unique=True)
            is_local = Required(bool, default=False)
            accounts = Set('Account', reverse='currency', cascade_delete=False)
            exchange_rates = Set('ExchangeRate', reverse='currency')

        class ExchangeRate(db.Entity):
            id = PrimaryKey(int, auto=True)  # 汇率唯一标识
            currency = Required(Currency)          # 币种
            rate = Required(float)                 # 汇率
            effective_date = Required(datetime.date) # 生效日期

        class Account(db.Entity):
            id = PrimaryKey(int, auto=True)  # 科目的唯一标识
            name = Required(str)                   # 科目名称
            qualname = Required(str, unique=True)  # 科目限定名
            code = Required(str, unique=True)      # 科目代码
            major_category = Required(str)         # 科目大类
            direction = Required(str)              # 借或贷
            currency = Optional(Currency)          # 币种
            need_exchange_gains_losses = Required(bool, default=False)        # 是否加入汇兑损益
            is_custom = Required(bool, default=True)                          # 是否为用户自定义科目
            parent = Optional('Account')                                      # 父科目，可以为 None，表示顶级科目
            children = Set('Account', reverse='parent')               # 子科目集合，reverse='parent' 表示从子科目反向查找父科目
            debit_entries = Set('DebitEntry', reverse='account')      # 借方条目集合
            credit_entries = Set('CreditEntry', reverse='account')    # 贷方条目集合

        # 定义 DebitEntry 实体，表示借方的具体条目
        class DebitEntry(db.Entity):
            id = PrimaryKey(int, auto=True)
            voucher = Required('Voucher')   # 关联的凭证
            account = Required(Account)     # 借方关联的科目
            currency = Required(str)        # 当时币种名称
            amount = Required(float)        # 借方币种金额
            exchange_rate = Required(float) # 借方当时汇率
            brief = Optional(str)           # 凭证描述

        # 定义 CreditEntry 实体，表示贷方的具体条目
        class CreditEntry(db.Entity):
            id = PrimaryKey(int, auto=True)
            voucher = Required('Voucher')   # 关联的凭证
            account = Required(Account)     # 贷方关联的科目
            currency = Required(str)        # 当时币种名称
            amount = Required(float)        # 贷方币种金额
            exchange_rate = Required(float) # 贷方当时汇率
            brief = Optional(str)           # 凭证描述

        # 定义 Voucher 实体类
        class Voucher(db.Entity):
            id = PrimaryKey(int, auto=True)    # 凭证的唯一编号
            number = Required(str, unique=True)      # 凭证编号，必须唯一
            category = Required(str, default='记账')  # 凭证类型  # 记账 # 月末结转 # 往年结转
            date = Required(datetime.date)           # 凭证日期
            debit_entries = Set(DebitEntry)          # 借方条目集合
            credit_entries = Set(CreditEntry)        # 贷方条目集合

        # Balance sheet
        class BalanceSheetTemplate(db.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str, unique=True)
            asset_liability_entries = Set('BalanceSheetEntry', reverse='template')

        class BalanceSheetEntry(db.Entity):
            id = PrimaryKey(int, auto=True)
            template = Required(BalanceSheetTemplate)
            category = Required(str)                  # 资产 / 负债和所有者权益（或股东权益）
            item = Optional(str)                      # 项目名称 / 可设为空行
            line_number = Optional(int)               # 行次
            formula = Optional(str)                   # 计算公式

        # -------- User data
        class MRU_Account(db.Entity):
            id = PrimaryKey(int, auto=True)
            account_code = Required(str, unique=True)
            hits = Required(int, default=0)

        db.bind(provider='sqlite', filename=str(filename), create_db=True)
        db.generate_mapping(create_tables=True)

        FFDB.db = db