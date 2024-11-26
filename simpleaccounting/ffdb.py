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


        class MetaData(db.Entity):
            id = PrimaryKey(int, auto=True)
            version = Required(str)
            company = Required(str)
            month_from = Required(datetime.date)
            month_until = Required(datetime.date)

        class Currency(db.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str, unique=True)
            accounts = Set('Account', reverse='currency', cascade_delete=False)
            exchange_rates = Set('ExchangeRate', reverse='currency')

        class ExchangeRate(db.Entity):
            id = PrimaryKey(int, auto=True)  # 汇率唯一标识
            currency = Required(Currency)          # 币种
            rate = Required(float)                 # 汇率
            effective_date = Required(datetime.date) # 生效日期
            debit_entries = Set('DebitEntry', reverse='exchange_rate', cascade_delete=False)
            credit_entries = Set('CreditEntry', reverse='exchange_rate', cascade_delete=False)

        class Account(db.Entity):
            id = PrimaryKey(int, auto=True)  # 科目的唯一标识
            name = Required(str, unique=True)      # 科目名称
            qualname = Required(str, unique=True)  # 科目限定名
            code = Required(str, unique=True)      # 科目代码
            major_category = Required(str)         # 科目大类
            sub_category = Required(str)           # 科目小类
            direction = Required(str)              # 借或贷
            currency = Optional(Currency)          # 币种
            exchange_gains_and_losses = Required(bool, default=False)    # 是否加入汇兑损益
            custom = Required(bool, default=True)                      # 是否为用户自定义科目
            parent = Optional('Account')                               # 父科目，可以为 None，表示顶级科目
            children = Set('Account', reverse='parent')        # 子科目集合，reverse='parent' 表示从子科目反向查找父科目
            debit_entries = Set('DebitEntry', reverse='account')      # 借方条目集合
            credit_entries = Set('CreditEntry', reverse='account')    # 贷方条目集合
            ending_balances = Set('Shadow_EndingBalance', reverse='account') # 结余条目集合

        # 定义 DebitEntry 实体，表示借方的具体条目
        class DebitEntry(db.Entity):
            id = PrimaryKey(int, auto=True)
            voucher = Required('Voucher')   # 关联的凭证
            account = Required(Account)     # 借方关联的科目
            amount = Required(float)        # 借方币种金额
            exchange_rate = Required(ExchangeRate) # 借方汇率
            brief = Optional(str)           # 凭证描述

        # 定义 CreditEntry 实体，表示贷方的具体条目
        class CreditEntry(db.Entity):
            id = PrimaryKey(int, auto=True)
            voucher = Required('Voucher')   # 关联的凭证
            account = Required(Account)     # 贷方关联的科目
            amount = Required(float)        # 贷方币种金额
            exchange_rate = Required(ExchangeRate) # 贷方汇率
            brief = Optional(str)           # 凭证描述

        # 定义 Voucher 实体类
        class Voucher(db.Entity):
            id = PrimaryKey(int, auto=True) # 凭证的唯一编号
            number = Required(str, unique=True)   # 凭证编号，必须唯一
            category = Required(str, default='记账')   # 凭证类型
            date = Required(datetime.date)        # 凭证日期
            debit_entries = Set(DebitEntry)       # 借方条目集合
            credit_entries = Set(CreditEntry)     # 贷方条目集合
            note = Optional(str)                  # 备注

        class Shadow_EndingBalance(db.Entity):
            id = PrimaryKey(int, auto=True)   # 结余唯一标识
            account = Required(Account)             # 关联的科目
            currency_amount = Required(float)       # 币种金额
            local_currency_amount = Required(float) # 本位币金额
            month = Required(datetime.date)          # 结余年月

        # -------- User data
        class MRU_Account(db.Entity):
            id = PrimaryKey(int, auto=True)
            account_code = Required(str, unique=True)
            hits = Required(int, default=0)

        class OperationLog(db.Entity):
            id = PrimaryKey(int, auto=True)
            entity_name = Required(str)
            operation_type = Required(str)
            commited = Required(bool, default=False)
            entity_id = Required(int)
            timestamp = Required(datetime.datetime)
            details = Required(str)


        # commited_cache = defaultdict(dict)

        # Generic function to attach event hooks to all entities
        # def attach_logging_hooks(db):
        #
        #     import types
        #
        #     for _, entity in db.entities.items():
        #         # Hook for insert
        #         def details(instance):
        #             return ','.join(f"{attr.name}={getattr(instance, attr.name)!r}" for attr in instance._attrs_ if attr.is_basic)
        #
        #         def log_insert(instance):
        #             if isinstance(instance, OperationLog):
        #                 return
        #             operation_log = OperationLog(entity_name=instance.__class__.__name__, operation_type='INSERT',
        #                          entity_id=instance.id, timestamp=datetime.datetime.now(),
        #                          details=details(instance),
        #                          commited=True)
        #             operation_log.flush()
        #
        #         def log_update(instance):
        #             if isinstance(instance, OperationLog):
        #                 return
        #             operation_log = OperationLog(entity_name=instance.__class__.__name__, operation_type='UPDATE',
        #                          entity_id=instance.id, timestamp=datetime.datetime.now(),
        #                          details=details(instance),
        #                          commited=True)
        #             operation_log.flush()
        #
        #         def log_before_delete(instance):
        #             if isinstance(instance, OperationLog):
        #                 return
        #             operation_log = OperationLog(entity_name=instance.__class__.__name__, operation_type='DELETE',
        #                          entity_id=instance.id, timestamp=datetime.datetime.now(),
        #                          details=details(instance),
        #                          commited=False)
        #             operation_log.flush()
        #             commited_cache[instance.__class__.__name__][instance.id] = operation_log.id
        #
        #         def log_after_delete(instance):
        #             if isinstance(instance, OperationLog):
        #                 return
        #             operation_log = OperationLog.get(id=commited_cache[instance.__class__.__name__][instance.id])
        #             operation_log.commited = True
        #             operation_log.flush()
        #
        #         entity.before_delete = log_before_delete
        #         entity.after_delete = log_after_delete
        #         entity.after_insert = log_insert
        #         entity.after_update = log_update
        #
        # # Attach the logging hooks
        # attach_logging_hooks(db)

        db.bind(provider='sqlite', filename=str(filename), create_db=True)
        db.generate_mapping(create_tables=True)

        FFDB.db = db