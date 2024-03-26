import beaker
import pyteal as pt

class AppState:
    # Global state
    organization = beaker.GlobalStateValue(
        stack_type = pt.TealType.bytes,
        descr = "Charity organization",
        default = pt.Bytes("")
    )

    cause = beaker.GlobalStateValue(
        stack_type = pt.TealType.bytes,
        descr = "Cause",
        default = pt.Bytes("")
    )

    wager = beaker.GlobalStateValue(
        stack_type = pt.TealType.uint64,
        descr = "Recources needed",
        default = pt.Int(0)
    )

    currently_raised = beaker.GlobalStateValue(
        stack_type = pt.TealType.uint64,
        descr = "Currently raised",
        default = pt.Int(0)
    )

    donor = beaker.GlobalStateValue(
        stack_type = pt.TealType.bytes,
        descr = "Donor",
        default = pt.Bytes("")
    )


    # Local state


app = beaker.Application("Charityverse", descr = "dApp for funding charitable causes", state=AppState)

# Methods

# create - initializes global state
@app.create(bare=True)
def create() -> pt.Expr:
    return app.initialize_global_state()

# opt-in
@app.opt_in(bare=True)
def opt_in() -> pt.Expr:
    return pt.Seq(
        pt.If(app.state.organization.get() == pt.Bytes(""))
        .Then(app.state.organization.set(pt.Txn.sender()))
        .ElseIf(app.state.wager.get() != pt.Int(0))
        .Then(app.state.donor.set(pt.Txn.sender()))
        .Else(pt.Reject()),
        app.initialize_local_state()
    )

@app.external(authorize=beaker.Authorize.opted_in())
def set_up_fundraiser(amount: pt.abi.Uint64, cause: pt.abi.String) -> pt.Expr:
    return pt.Seq(
        pt.Assert(pt.Txn.sender() == app.state.organization),
        app.state.wager.set(amount.get()),
        app.state.cause.set(cause.get())
    )

@app.external(authorize=beaker.Authorize.opted_in())
def donate(payment: pt.abi.PaymentTransaction, *, output: pt.abi.String) -> pt.Expr:
    return pt.Seq(
        pt.Assert(
            app.state.cause.get() != pt.Bytes(""),
            payment.type_spec().txn_type_enum() == pt.TxnType.Payment,
            payment.get().receiver() == pt.Global.current_application_address()
        ),
        app.state.currently_raised.set(pt.Add(app.state.currently_raised.get(), payment.get().amount())),
        output.set(pt.Bytes("Hvala Vam na donaciji"))
    )
