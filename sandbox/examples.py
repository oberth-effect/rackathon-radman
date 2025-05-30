scenario_1 = {
    'patients': [
        Patient(id="a", weight=81, procedure=PROC[Timestamp.FDGO]),
        Patient(id="b", weight=80, procedure=PROC[Timestamp.FDGO]),
        Patient(id="c", weight=75, procedure=PROC[Timestamp.FDGO]),
        Patient(id="d", weight=102, procedure=PROC[Timestamp.FDGO]),
        Patient(id="e", weight=74, procedure=PROC[Timestamp.FDGO]),
        Patient(id="f", weight=75, procedure=PROC[Timestamp.FDGO]),
        Patient(id="g", weight=78, procedure=PROC[Timestamp.FDGO]),
        Patient(id="h", weight=66, procedure=PROC[Timestamp.FDGO]),
    ],
    'counts': [8, 0, 0, 0, 0, 0],
    # 'schedule': [(time, (procedura, patient))]
    'schedule': [(time(7,35), 'a'),
                 (time(8,7),  'b'),
                 (time(8,38), 'g'),
                 (time(9,16), 'e'),
                 (time(9,55), 'd'),
                 (time(10,22), 'f'),
                 (time(11,01), 'h')
                 ]
}

scenario_2 = {
    'patients': [
        Patient(id="a", weight=61, procedure=PROC[Timestamp.FDGO]),
        Patient(id="b", weight=85, procedure=PROC[Timestamp.FDGO]),
        Patient(id="c", weight=66, procedure=PROC[Timestamp.FDGO]),
        Patient(id="d", weight=80, procedure=PROC[Timestamp.FDGO]),
        Patient(id="e", weight=62, procedure=PROC[Timestamp.FDGO]),
        Patient(id="f", weight=73, procedure=PROC[Timestamp.FDGO]),
        Patient(id="g", weight=65, procedure=PROC[Timestamp.FDGO]),
        Patient(id="h", weight=65, procedure=PROC[Timestamp.FDGO]),
    ],
    'counts': [8, 0, 0, 0, 0, 0],
    'schedule': [(time(7,40), 'a'),
                 (time(8,15),  'b'),
                 (time(8,57), 'c'),
                 (time(9,23), 'e'),
                 (time(9,48), 'c'),
                 (time(10,26), 'f'),
                 (time(11,0), 'g')
                 ]
}

scenario_3 = {
    'patients': [
        Patient(id="a", weight=66, procedure=PROC[Timestamp.FDGO]),
        Patient(id="b", weight=70, procedure=PROC[Timestamp.FDGO]),
        Patient(id="c", weight=78, procedure=PROC[Timestamp.FDGO]),
        Patient(id="d", weight=70, procedure=PROC[Timestamp.FDGO]),
        Patient(id="e", weight=86, procedure=PROC[Timestamp.FDGO]),
        Patient(id="f", weight=59, procedure=PROC[Timestamp.FDGO]),
        Patient(id="g", weight=60, procedure=PROC[Timestamp.FDGO]),
        Patient(id="h", weight=88, procedure=PROC[Timestamp.FDGO]),
    ],
    'counts': [8, 0, 0, 0, 0, 0],
    'schedule': [(time(7,56), 'a'),
                 (time(8,37), 'b'),
                 (time(9,9), 'f'),
                 (time(9,41), 'c'),
                 (time(10,19), 'd'),
                 (time(10,51), 'e'),
                 (time(11,34), 'g'),
                 (time(12,16), 'h')
                 ]
}

scenario_4 = {
    'patients': [
        Patient(id="a", weight=78, procedure=PROC[Timestamp.FDGO]),
        Patient(id="b", weight=67, procedure=PROC[Timestamp.FDGO]),
        Patient(id="c", weight=53, procedure=PROC[Timestamp.FDGO]),
        Patient(id="d", weight=92, procedure=PROC[Timestamp.FDGO]),
        Patient(id="e", weight=97, procedure=PROC[Timestamp.FDGO]),
        Patient(id="f", weight=98, procedure=PROC[Timestamp.FDGO]),
        Patient(id="g", weight=52, procedure=PROC[Timestamp.FDGO]),
        Patient(id="h", weight=60, procedure=PROC[Timestamp.FDGO]),
        Patient(id="i", weight=73, procedure=PROC[Timestamp.FDGO]),
        Patient(id="j", weight=54, procedure=PROC[Timestamp.FDGO]),
        Patient(id="k", weight=83, procedure=PROC[Timestamp.FDGO]),

    ],
    'counts': [11, 0, 0, 0, 0, 0],
    'schedule': [(time(7,43), 'f'),
                 (time(8,14), 'a'),
                 (time(8,40), 'g'),
                 (time(9,5), 'i'),
                 (time(9,35), 'd'),
                 (time(10,20), 'b'),
                 (time(10,50), 'c'),
                 (time(11,40), 'e'),
                 (time(12,40), 'h'),
                 (time(13,20), 'j'),
                 (time(13,58), 'k')
                 ]
}

scenario_5 = {
    'patients': [
        Patient(id="a", weight=67, procedure=PROC[Timestamp.FDGO]),
        Patient(id="b", weight=62, procedure=PROC[Timestamp.FDGO]),
        Patient(id="c", weight=64, procedure=PROC[Timestamp.FDGO]),
        Patient(id="d", weight=91, procedure=PROC[Timestamp.FDGO]),
        Patient(id="e", weight=98, procedure=PROC[Timestamp.FDGO]),
        Patient(id="f", weight=110, procedure=PROC[Timestamp.FDGO]),
        Patient(id="g", weight=70, procedure=PROC[Timestamp.FDGO]),
        Patient(id="h", weight=97, procedure=PROC[Timestamp.FDGO]),
        Patient(id="i", weight=80, procedure=PROC[Timestamp.FDGO]),
        Patient(id="j", weight=76, procedure=PROC[Timestamp.SomaKit]),
        Patient(id="k", weight=100, procedure=PROC[Timestamp.SomaKit]),
    ],
    'counts': [9, 0, 0, 0, 2, 0],
    'schedule': [(time(7,37), 'd'),
                 (time(8,25), 'f'),
                 (time(8,58), 'h'),
                 (time(9,25), 'e'),
                 (time(9,57), 'a'),
                 (time(10,49), 'b'),
                 (time(11,29), 'g'),
                 (time(12,0), 'i'),
                 (time(12,30), 'j'),
                 (time(13,2), 'k')
                 ]
}