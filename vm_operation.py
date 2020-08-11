"""
    This file describes a list of operations to be executed against the instance server

    The operation Object List is created so it makes the induced life cycle.

    The instance server is created, then suspended, reactivated, stopped and then  shelved.

    These operations are highly parameterized. Be careful so the rules (targed and required status) are respected


    Each operation object must contain:

        operation: The operation name. Conventions to upper case. Ex.: CREATE, SHELVE, STOP...
        targetStatus: The status that should be reached when the operation is executed.
                        Ex.: CREATE operation hits ACTIVE state. Thus {operation: 'CREATE', targetStatus: 'ACTIVE'}
        requiredStatus: List of possible vm states that allows the operation to be executed.
                        Ex.: SUSPEND operation must be executed only when the current vm state shows 'ACTIVE' or 'SHUTOFF'.
                            Thus {operation: 'SUSPEND', targetStatus: 'SUSPENDED', 'requiredStatus': ['ACTIVE', 'SHUTOFF']}
        anonymousFunction: lambda function that will be executed. It represents the operation execution and takes the server as argument.
                           Other implementations may use the actual server to execute the operation. It would look like server.create(), for example.

"""

operationObjectList = [
    {
        'operation':'CREATE',
        'targetStatus':'ACTIVE',
        'requiredStatus':['BUILD'], #Note: OpenStack should refactor this status to INITIALIZE
        'params':{'flavor':'m1.xlarge'}
    },
    {
        'operation':'SUSPEND',
        'targetStatus':'SUSPENDED',
        'requiredStatus':['ACTIVE','SHUTOFF'],
        'anonymousFunction':lambda compute, server: compute.suspend_server(server)
    },
    {
        'operation':'RESUME',
        'targetStatus':'ACTIVE',
        'requiredStatus':['SUSPENDED'],
        'anonymousFunction':lambda compute, server: compute.resume_server(server)
    },
    {
        'operation':'STOP',
        'targetStatus':'SHUTOFF', #STOPPED
        'requiredStatus':['ACTIVE','SHUTOFF', 'RESCUED'],
        'anonymousFunction':lambda compute, server: compute.stop_server(server)
    },
    {
        'operation':'SHELVE',
        'targetStatus':'SHELVED_OFFLOADED',
        'requiredStatus':['ACTIVE', 'SHUTOFF', 'SUSPENDED', 'STOPPED'],
        'anonymousFunction':lambda compute, server: compute.shelve_server(server)
    }
]
