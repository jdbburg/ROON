<script>
    export let nodes = [];

    nodes.push({
        name: 'variable',
        inputs: [
            {name: 'value', type: 'any', default: 0}
        ],
        outputs: [
            {name: 'value', type: 'number', value: 0}
        ],
        source: ''
    });
    nodes.push(
        {
            name: 'add',
            inputs: [
                {name: 'a', type: 'number', default: 0},
                {name: 'b', type: 'number', default: 0}
            ],
            outputs: [
                {name: 'value', type: 'number', value: 0}
            ],
            sourceTemplate: 'f"value = {a} + {b}"'
        }
    )

</script>