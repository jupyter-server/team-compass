"""Generate HTML Contributors tables for team pages
"""
import pathlib
import pandas as pd
import os
import os.path as op
from ruamel import yaml

# Variables
N_PER_ROW = 4

# Init
path_data = op.join(op.dirname(op.abspath(__file__)), "..", "team")
yaml = yaml.YAML()

template = '<td align="center" class="contrib_entry"><a href="{HANDLE_URL}"><img src="{AVATAR_URL}" class="headshot" alt="{NAME}" /><br /><p class="name"><b>{NAME}</b></p></a><p class="contrib_affiliation">{AFFILIATION}</p>'


def _generate_contributors(contributors):
    """Generate an HTML list of contributors, given a dataframe of their information."""
    s = ['<table class="docutils contributors">', '<tr class="row-even">']
    for ix, person in contributors.iterrows():
        if ix % N_PER_ROW == 0 and ix != 0:
            s += ['</tr><tr class="row-even">']

        # Find user gravatar url
        avatar_url = "https://github.com/{HANDLE}.png?size=200".format(
            HANDLE=person["handle"].lstrip("@")
        )

        # Add user
        format_dict = dict(
            HANDLE=person["handle"],
            HANDLE_URL="https://github.com/{HANDLE}".format(
                HANDLE=person["handle"].lstrip("@")
            ),
            AFFILIATION=person["affiliation"],
            AVATAR_URL=avatar_url,
            NAME=person["name"],
        )

        # Render
        s += [template.format(**format_dict)]
    s += ["</table>"]
    final_text = [".. raw:: html", ""]
    for line in s:
        final_text += ["   " + line]
    final_text = "\n".join(final_text)
    return final_text

# Load contributor list
source_dir = pathlib.Path(path_data)
contributor_file = source_dir / "contributors-jupyter-server.yaml"
with open(contributor_file, "r") as ff:
    data = yaml.load(ff)

people = pd.DataFrame(data)

# Create active member table
active_people = people[people.team == "active"]
table = _generate_contributors(active_people)
with open(source_dir / "active.txt", "w") as ff:
    ff.write(table)

# Create inactive member table
inactive_people = people[people.team == "inactive"]
table = _generate_contributors(inactive_people)
with open(source_dir / "inactive.txt", "w") as ff:
    ff.write(table)

# Find past and current SSC representatives
ssc_reps = people[people.ssc.notna()]
for index, rep in ssc_reps.iterrows():
    # Fetch the latest term
    latest_term = rep.ssc[-1]
    # Split date and check if there is an end date.
    is_current = latest_term.split("-")[-1] == ""
    if is_current:
        break

table = _generate_contributors(rep.to_frame().T)
with open(source_dir / "ssc-current.txt", "w") as ff:
    ff.write(table)

table = _generate_contributors(ssc_reps.drop(index))
with open(source_dir / "ssc-past.txt", "w") as ff:
    ff.write(table)
