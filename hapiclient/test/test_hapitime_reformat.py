import os
from hapiclient.hapi import hapitime_reformat

# See comments in test_hapitime2datetime.py for execution options.

def test_hapitime_reformat():


    dts = [
        "1989Z",

        "1989-01Z",

        "1989-001Z",
        "1989-01-01Z",

        "1989-001T00Z",
        "1989-01-01T00Z",

        "1989-001T00:00Z",
        "1989-01-01T00:00Z",

        "1989-001T00:00:00.Z",
        "1989-01-01T00:00:00.Z",

        "1989-01-01T00:00:00.0Z",
        "1989-001T00:00:00.0Z",

        "1989-01-01T00:00:00.00Z",
        "1989-001T00:00:00.00Z",

        "1989-01-01T00:00:00.000Z",
        "1989-001T00:00:00.000Z",

        "1989-01-01T00:00:00.0000Z",
        "1989-001T00:00:00.0000Z",

        "1989-01-01T00:00:00.00000Z",
        "1989-001T00:00:00.00000Z",

        "1989-01-01T00:00:00.000000Z",
        "1989-001T00:00:00.000000Z",

        "1989-01-01T00:00:00.0000000Z",
        "1989-001T00:00:00.0000000Z",

        "1989-01-01T00:00:00.00000000Z",
        "1989-001T00:00:00.00000000Z",

        "1989-01-01T00:00:00.000000000Z",
        "1989-001T00:00:00.000000000Z"
    ]


    for i in range(len(dts)):
        if "T" in dts[i]:
            dts.append("1989-001T" + dts[i].split("T")[1])

    logging = open(os.path.realpath(__file__)[0:-2] + "log", "w")

    # truncating
    for i in range(len(dts)):
        form_to_match = dts[i]
        for j in range(i + 1, len(dts)):
            given_form = dts[j]
            given_form_modified = hapitime_reformat(form_to_match, given_form, logging=logging)
            assert given_form_modified == form_to_match
            
    # padding
    dts = list(reversed(dts))
    for i in range(len(dts)):
        form_to_match = dts[i]
        for j in range(i + 1, len(dts)):
            given_form = dts[j]
            given_form_modified = hapitime_reformat(form_to_match, given_form, logging=logging)
            assert given_form_modified == form_to_match

    logging.close()

if __name__ == '__main__':
    test_hapitime_reformat()
