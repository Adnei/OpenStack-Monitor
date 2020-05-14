operationObjectList = [
    {
        'operation':'CREATE',
        'targetStatus':'ACTIVE',
        'requiredStatus':['BUILD'], #Note: OpenStack should refactor this status to INITIALIZE
        'params':{'flavor':'m1.small'}
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
