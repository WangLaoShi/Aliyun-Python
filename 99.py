print('\n'.join(
    ['\t'.join(
        [f"{i}*{j}={i * j}" for j in range(1, i + 1)]
        )
        for i in range(1, 10)
    ]
) )
