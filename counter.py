from pyteal import *
from pyteal.ast import Bytes
from pyteal_helpers import program

global_counter = Bytes("counter")  # int
global_owner = Bytes("owner")

op_inc = Bytes("inc")
op_dec = Bytes("dec")

increment = Seq(
            App.globalPut(global_counter, App.globalGet(global_counter)+Int(1)),
            Approve()
        )
decrement = Seq(
            App.globalPut(global_counter, App.globalGet(global_counter)-Int(1)),
            Approve()
        )


p0 = Bytes("p0")  # byteslice
p1 = Bytes("p1")  # byteslice
p2 = Bytes("p2")  # byteslice
client = Bytes("client")  # byteslice

p0_share = Bytes("p0_share")  # uint64
p1_share = Bytes("p1_share")  # uint64
p2_share = Bytes("p2_share")  # uint64


def approval():
    local_wager = Bytes("wager")  # uint64


    op_accept_player_input = Bytes("accept_player_input")
    op_reveal = Bytes("reveal")

    @Subroutine(TealType.none)
    def reset(account: Expr):
        return Seq(
            App.globalPut(p0, Bytes("")),
            App.globalPut(p1, Bytes("")),
            App.globalPut(p2, Bytes("")),
            App.globalPut(client, Bytes("")),
            App.globalPut(p0_share, Int(0)),
            App.globalPut(p1_share, Int(0)),
            App.globalPut(p2_share, Int(0)),
            # App.localPut(account, local_wager, Int(0)),
            # App.localPut(account, local_commitment, Bytes("")),
            # App.localPut(account, local_reveal, Bytes("")),
        )

    @Subroutine(TealType.none)
    def create_challenge():
        return Seq(
            # basic sanity checks
            # program.check_self(
            #     group_size=Int(2),
            #     group_index=Int(0),
            # ),
            # program.check_rekey_zero(2),
            # Assert(
            #     And(
            #         # second transaction is wager payment
            #         Gtxn[1].type_enum() == TxnType.Payment,
            #         Gtxn[1].receiver() == Global.current_application_address(),
            #         Gtxn[1].close_remainder_to() == Global.zero_address(),
            #         # second account has opted-in
            #         App.optedIn(Int(1), Int(0)),
            #         is_empty(Int(1)),
            #         # commitment
            #         Txn.application_args.length() == Int(2),
            #     )
            # ),
            App.localPut(Txn.sender(), local_opponent, Txn.accounts[1]),
            App.localPut(Txn.sender(), local_wager, Gtxn[1].amount()),
            App.localPut(
                Txn.sender(),
                local_commitment,
                Txn.application_args[1],
            ),
            Approve(),
        )

    @Subroutine(TealType.none)
    def putP0sShare():
        return Seq(
            App.globalPut(p0_share, Txn.application_args[2]),
            # Assert(App.globalGet(p0) == Bytes("KVSQP35QS6TD3MOLFMXXMBU6VXVY7MWSAN2S6JNBXTVXMV4J566IGNHECY")),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: Int(3333000000),
                    TxnField.fee: Int(1000),  # use fee pooling
                }
            ),
            InnerTxnBuilder.Submit(),
            Approve(),
        )

    @Subroutine(TealType.none)
    def putP1sShare():
        return Seq(
            App.globalPut(p1_share, Txn.application_args[2]),
            # Assert(App.globalGet(p0) == Bytes("KVSQP35QS6TD3MOLFMXXMBU6VXVY7MWSAN2S6JNBXTVXMV4J566IGNHECY")),
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[1],
                    TxnField.amount: Int(3333),
                    TxnField.fee: Int(1000),  # use fee pooling
                }
            ),
            InnerTxnBuilder.Submit(),
            Approve(),
        )

    @Subroutine(TealType.none)
    def putP2sShare():
        return Seq(
            App.localPut(Txn.sender(), p2_share, Txn.application_args[2]),
            Approve(),
        )

    # accepting player input
    # @Subroutine(TealType.none)
    # def accept_player_input():
    accept_player_input = Seq(
            # Approve(),
                Cond(
                    [
                        Txn.application_args[1] == p0,
                        putP0sShare(),
                    ],
                    [
                        Txn.application_args[1] == p1,
                        putP1sShare(),
                    ],
                    [
                        Txn.application_args[1] == p2,
                        putP2sShare(),
                    ],
                ),
                Reject(),
            )

    # send player their reward
    @Subroutine(TealType.none)
    def send_reward(account_index: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[account_index],
                    TxnField.amount: amount,
                    TxnField.fee: Int(0),  # use fee pooling
                }
            ),
            InnerTxnBuilder.Submit(),
        )

    return program.event(
            init=Seq(
                App.globalPut(global_counter, Int(0)),
                App.globalPut(global_owner, Txn.sender()),
                Approve()
            ),
            opt_in=Seq(
                reset(Int(0)),
                Approve(),
            ),
            no_op=Cond(
                [Txn.application_args[0] == op_inc, increment],
                [Txn.application_args[0] == op_dec, decrement],
                [Txn.application_args[0] == op_accept_player_input, accept_player_input]
                )
            )

def clear():
    return Approve()

